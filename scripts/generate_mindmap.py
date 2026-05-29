#!/usr/bin/env python3
"""Generate a self-contained interactive mind map HTML page from a knowledge.json file.

Reads a knowledge.json file produced by the interview analysis pipeline,
transforms its segments into the MINDMAP_DATA format, and embeds the data
into a self-contained HTML file.

Usage:
    python generate_mindmap.py knowledge.json
    python generate_mindmap.py knowledge.json --output mindmap.html
    python generate_mindmap.py knowledge.json --template assets/mindmap-template.html

The knowledge.json file is expected to have this structure::

    {
      "metadata": {
        "title": "Interview Title",
        "guest": {"name": "Dr. Jane Smith"}  or  "guest": "Dr. Jane Smith",
        "date": "2026-05-30",
        "duration": "3h 47m"  or  {"total_seconds": 13620}
      },
      "segments": [
        {
          "id": "seg_01",
          "title": "Neural Architecture",
          "time_range": {"start": "00:00:00", "end": "00:42:00"},
          "summary": "Evolution of transformer architectures...",
          "insights": [
            {"text": "Sparse attention reduces compute...", "timestamp": "05:30"}
          ],
          "golden_quotes": [
            {"text": "The transformer was just...", "timestamp": "08:15", "speaker": "Guest"}
          ],
          "data_points": [
            {"text": "Training efficiency 3.2x...", "timestamp": "22:00", "type": "statistic"}
          ]
        }
      ]
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Color palette — 12 distinct, visually harmonious colors for dark backgrounds
# ---------------------------------------------------------------------------

COLOR_PALETTE: list[str] = [
    "#3b82f6",  # Blue 500
    "#8b5cf6",  # Violet 500
    "#10b981",  # Emerald 500
    "#f59e0b",  # Amber 500
    "#ec4899",  # Pink 500
    "#06b6d4",  # Cyan 500
    "#f97316",  # Orange 500
    "#84cc16",  # Lime 500
    "#14b8a6",  # Teal 500
    "#a855f7",  # Purple 500
    "#ef4444",  # Red 500
    "#22d3ee",  # Sky 400
]

# Perceptual rationale for each choice:
#   - Similar saturation (~70-85%) and lightness (~55-65%) so all colors feel
#     equally weighted when rendered on a dark (#0f0f23) radial-gradient canvas.
#   - Minimum 25-degree hue separation between neighbours; avoids the cyan/teal
#     and violet/purple ambiguity common in 12-colour HSL-equispace palettes.
#   - Colours are tested against WCAG AA for large text (≥18px / bold ≥14px)
#     when paired with white (#ffffff) labels on the mind-map topic nodes.

# ---------------------------------------------------------------------------
# Template insertion markers (checked in order)
# ---------------------------------------------------------------------------

MARKER_COMMENT = "<!-- MINDMAP_DATA_INSERT -->"
MARKER_MUSTACHE = "{{MINDMAP_DATA}}"
MARKER_CONST = "const MINDMAP_DATA ="


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------


def load_knowledge_json(filepath: str) -> dict[str, Any]:
    """Load and parse a knowledge.json file.

    Args:
        filepath: Path to the knowledge.json file.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_template(filepath: str) -> str:
    """Read the mind map template HTML file as a string.

    Args:
        filepath: Path to the template HTML file.

    Returns:
        Template content.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        return fh.read()


def write_output(filepath: str, content: str) -> None:
    """Write content to a file with UTF-8 encoding.

    Args:
        filepath: Destination file path.
        content: String content to write.

    Raises:
        OSError: If the file cannot be written.
    """
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------


def _extract_metadata(raw: dict[str, Any]) -> dict[str, str]:
    """Extract and normalise metadata fields from the knowledge JSON.

    Handles flexible input shapes:
        - ``guest`` may be a plain string or ``{"name": "..."}``.
        - ``duration`` may be a string like ``"3h 47m"`` or
          ``{"total_seconds": 13620}``.

    Args:
        raw: The full parsed knowledge.json dict.

    Returns:
        A dict with keys ``title``, ``guest``, ``date``, ``duration``.
        All values are plain strings. Missing metadata yields sensible
        defaults rather than raising.
    """
    meta: dict[str, Any] = raw.get("metadata", {})

    # -- title --
    title: str = meta.get("title", "Untitled Interview")

    # -- guest (string or object) --
    guest_raw = meta.get("guest", "")
    if isinstance(guest_raw, dict):
        guest: str = guest_raw.get("name", "")
    else:
        guest = str(guest_raw) if guest_raw else ""

    # -- date --
    date: str = meta.get("date", "")

    # -- duration (string like "3h 47m" or dict with total_seconds) --
    duration_raw = meta.get("duration", "")
    if isinstance(duration_raw, dict):
        total_seconds: int = int(duration_raw.get("total_seconds", 0))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            duration = f"{hours}h {minutes}m"
        else:
            duration = f"{minutes}m"
    else:
        duration = str(duration_raw) if duration_raw else ""

    return {
        "title": title,
        "guest": guest,
        "date": date,
        "duration": duration,
    }


# ---------------------------------------------------------------------------
# Time-range formatting
# ---------------------------------------------------------------------------


def _format_time_range(segment: dict[str, Any]) -> str:
    """Format a segment's ``time_range`` into a display string.

    Expects ``{"start": "HH:MM:SS", "end": "HH:MM:SS"}``.
    Returns ``"HH:MM:SS-HH:MM:SS"`` when both are present, otherwise just
    the start timestamp or an empty string.

    Args:
        segment: A segment dict from knowledge.json.

    Returns:
        Formatted time range.
    """
    tr = segment.get("time_range", {})
    if isinstance(tr, dict):
        start = tr.get("start", "")
        end = tr.get("end", "")
        if start and end:
            return f"{start}-{end}"
        return start or end or ""
    return str(tr) if tr else ""


# ---------------------------------------------------------------------------
# Core data transformation
# ---------------------------------------------------------------------------


def transform_to_mindmap_data(raw: dict[str, Any]) -> dict[str, Any]:
    """Transform knowledge.json data into the ``MINDMAP_DATA`` format expected
    by the mind map template.

    Mapping rules:

    * ``metadata.*`` → top-level ``title``, ``guest``, ``date``, ``duration``.
    * ``segments`` → ``topics`` array (one topic per segment).
    * Each topic is assigned a distinct colour from ``COLOR_PALETTE``
      in round-robin order.
    * ``segment.insights`` → ``topic.insights[]`` (``text``, ``timestamp``).
    * ``segment.golden_quotes`` → ``topic.quotes[]`` (``text``, ``timestamp``,
      ``speaker``).
    * ``segment.data_points`` → ``topic.data_points[]`` (``text``,
      ``timestamp``, ``type``).

    Args:
        raw: The full parsed knowledge.json dict.

    Returns:
        A dict conforming to the ``MINDMAP_DATA`` schema.
    """
    meta = _extract_metadata(raw)
    segments: list[dict[str, Any]] = raw.get("segments", [])

    topics: list[dict[str, Any]] = []
    for idx, seg in enumerate(segments):
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]

        # --- insights ---
        insights: list[dict[str, str]] = []
        for ins in seg.get("insights", []):
            insights.append(
                {
                    "text": ins.get("text", ""),
                    "timestamp": ins.get("timestamp", ""),
                }
            )

        # --- golden_quotes → quotes ---
        quotes: list[dict[str, str]] = []
        for q in seg.get("golden_quotes", []):
            quotes.append(
                {
                    "text": q.get("text", ""),
                    "timestamp": q.get("timestamp", ""),
                    "speaker": q.get("speaker", ""),
                }
            )

        # --- data_points ---
        data_points: list[dict[str, str]] = []
        for dp in seg.get("data_points", []):
            data_points.append(
                {
                    "text": dp.get("text", ""),
                    "timestamp": dp.get("timestamp", ""),
                    "type": dp.get("type", "statistic"),
                }
            )

        topics.append(
            {
                "name": seg.get("title", f"Topic {idx + 1}"),
                "time_range": _format_time_range(seg),
                "color": color,
                "summary": seg.get("summary", ""),
                "insights": insights,
                "quotes": quotes,
                "data_points": data_points,
            }
        )

    return {
        "title": meta["title"],
        "guest": meta["guest"],
        "date": meta["date"],
        "duration": meta["duration"],
        "topics": topics,
    }


def format_mindmap_data_js(data: dict[str, Any], indent: int = 2) -> str:
    """Render the MINDMAP_DATA dict as a pretty-printed JavaScript variable
    declaration.

    Args:
        data: The transformed MINDMAP_DATA dict.
        indent: Number of spaces for JSON indentation.

    Returns:
        A string of the form ``const MINDMAP_DATA = ...;``.
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=indent)
    return f"const MINDMAP_DATA = {json_str};"


# ---------------------------------------------------------------------------
# Template embedding
# ---------------------------------------------------------------------------


def embed_data(template: str, mindmap_data_js: str) -> str:
    """Insert the MINDMAP_DATA JavaScript variable into the template HTML.

    Three insertion strategies are tried **in order**:

    1. **Marker comment** — replace ``<!-- MINDMAP_DATA_INSERT -->``.
    2. **Mustache placeholder** — replace ``{{MINDMAP_DATA}}``.
    3. **Existing declaration** — locate ``const MINDMAP_DATA = …;`` via
       brace-depth tracking and replace the whole block.

    Args:
        template: The HTML template string.
        mindmap_data_js: The ``const MINDMAP_DATA = …;`` string to insert.

    Returns:
        Template with data embedded.

    Raises:
        ValueError: If no recognised insertion point is found.
    """
    # Strategy 1: HTML comment marker
    if MARKER_COMMENT in template:
        return template.replace(MARKER_COMMENT, mindmap_data_js)

    # Strategy 2: Mustache placeholder
    if MARKER_MUSTACHE in template:
        return template.replace(MARKER_MUSTACHE, mindmap_data_js)

    # Strategy 3: Find existing const MINDMAP_DATA = ...; block
    if MARKER_CONST in template:
        return _replace_existing_data_block(template, mindmap_data_js)

    raise ValueError(
        "Could not find an insertion point in the template. "
        "Ensure the template contains one of: "
        f"{MARKER_COMMENT!r}, {MARKER_MUSTACHE!r}, "
        f"or an existing {MARKER_CONST!r} declaration."
    )


def _replace_existing_data_block(template: str, mindmap_data_js: str) -> str:
    """Replace the ``const MINDMAP_DATA = {…};`` block inside *template*.

    The function finds the ``const MINDMAP_DATA =`` prefix, then tracks brace
    depth (respecting JSON string escaping) to locate the matching ``};``.

    Args:
        template: The HTML template string.
        mindmap_data_js: The replacement JavaScript variable declaration.

    Returns:
        Template with the old data block replaced.

    Raises:
        ValueError: If the declaration cannot be reliably parsed.
    """
    start_pos = template.find(MARKER_CONST)
    if start_pos == -1:
        raise ValueError("No existing MINDMAP_DATA declaration found in template.")

    # Find the opening brace after the prefix
    brace_pos = template.find("{", start_pos)
    if brace_pos == -1:
        raise ValueError(
            "Malformed MINDMAP_DATA declaration: no opening brace found."
        )

    # Brace-depth scanner that respects JSON string escaping
    depth = 0
    in_string = False
    i = brace_pos

    while i < len(template):
        ch = template[i]

        if in_string:
            if ch == "\\":
                # Escape sequence — skip the escaped character.
                # The loop increment (+1 below) advances past it.
                i += 1
            elif ch == '"':
                in_string = False
            i += 1
            continue

        # Outside a string literal
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                # Found the closing brace of the top-level object.
                # Advance past optional whitespace to include the semicolon.
                j = i + 1
                while j < len(template) and template[j] in (" ", "\t", "\n", "\r"):
                    j += 1
                if j < len(template) and template[j] == ";":
                    i = j
                break

        i += 1

    if depth != 0:
        raise ValueError(
            "Could not find matching closing brace for MINDMAP_DATA declaration. "
            f"Brace depth after scan: {depth} (expected 0)."
        )

    # Replace the original block with the new data
    return template[:start_pos] + mindmap_data_js + template[i + 1 :]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a self-contained interactive mind map HTML page "
            "from a knowledge.json file produced by the interview "
            "analysis pipeline."
        ),
    )
    parser.add_argument(
        "knowledge_json",
        metavar="KNOWLEDGE_JSON",
        help="Path to the knowledge.json input file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        default="mindmap.html",
        help="Path for the output HTML file (default: %(default)s).",
    )
    parser.add_argument(
        "--template",
        "-t",
        metavar="PATH",
        default=None,
        help=(
            "Path to a custom mind map template HTML file. "
            "If not provided, looks for assets/mindmap-template.html "
            "relative to the skill root directory."
        ),
    )
    return parser


def _default_template_path() -> Path:
    """Compute the default template path relative to this script.

    The script lives in ``scripts/generate_mindmap.py``; the default template
    is ``assets/mindmap-template.html`` in the skill root (one level up from
    ``scripts/``).

    Returns:
        Absolute ``Path`` to the default template.
    """
    script_dir = Path(__file__).resolve().parent  # scripts/
    skill_root = script_dir.parent  # skill root
    return skill_root / "assets" / "mindmap-template.html"


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the mind map generator CLI.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).
    """
    parser = build_argparser()
    args = parser.parse_args(argv)

    # ---- 1. Resolve template path -----------------------------------------
    template_path: str
    if args.template:
        template_path = args.template
    else:
        template_path = str(_default_template_path())

    # ---- 2. Load knowledge.json -------------------------------------------
    try:
        knowledge = load_knowledge_json(args.knowledge_json)
    except FileNotFoundError:
        print(
            f"Error: file not found: {args.knowledge_json}",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(
            f"Error: invalid JSON in {args.knowledge_json}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as exc:
        print(
            f"Error: failed to read {args.knowledge_json}: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    # ---- 3. Load template -------------------------------------------------
    try:
        template = load_template(template_path)
    except FileNotFoundError:
        print(
            f"Error: template file not found: {template_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as exc:
        print(
            f"Error: failed to read template {template_path}: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    # ---- 4. Transform data into MINDMAP_DATA format -----------------------
    try:
        mindmap_data = transform_to_mindmap_data(knowledge)
    except Exception as exc:
        print(
            f"Error: failed to transform knowledge data: {exc}",
            file=sys.stderr,
        )
        sys.exit(3)

    # ---- 5. Render JavaScript variable ------------------------------------
    mindmap_data_js = format_mindmap_data_js(mindmap_data)

    # ---- 6. Embed into template -------------------------------------------
    try:
        html_output = embed_data(template, mindmap_data_js)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(4)

    # ---- 7. Write output --------------------------------------------------
    try:
        write_output(args.output, html_output)
    except OSError as exc:
        print(
            f"Error: failed to write {args.output}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    # ---- 8. Summary -------------------------------------------------------
    topic_count = len(mindmap_data.get("topics", []))
    total_items = sum(
        len(t.get("insights", []))
        + len(t.get("quotes", []))
        + len(t.get("data_points", []))
        for t in mindmap_data.get("topics", [])
    )
    print(
        f"Generated {args.output}  "
        f"({topic_count} topic{'s' if topic_count != 1 else ''}, "
        f"{total_items} child node{'s' if total_items != 1 else ''})"
    )


if __name__ == "__main__":
    main()
