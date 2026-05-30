#!/usr/bin/env python3
"""Generate a self-contained interactive mind map HTML page from a visual_content.json file.

Reads a visual_content.json file produced by the interview analysis pipeline,
extracts its map_data for the mindmap structure, and embeds the data
into a self-contained HTML file.

Metadata (title, guest, date, duration) can be sourced from an optional
knowledge.json file, or extracted from the visual_content.json ``meta`` field
as a fallback.

Usage:
    python generate_mindmap.py visual_content.json
    python generate_mindmap.py visual_content.json --knowledge-json knowledge.json
    python generate_mindmap.py visual_content.json --output mindmap.html
    python generate_mindmap.py visual_content.json --template assets/mindmap-template.html

The visual_content.json file is expected to have this structure::

    {
      "meta": {
        "core_thesis": "...",
        "duration_formatted": "3h 47m",
        "stats": {"theme_count": 7, "segment_count": 12, ...}
      },
      "themes": [...],
      "segments": [...],
      "map_data": {
        "central_thesis": "core thesis text",
        "theme_nodes": [
          {
            "id": "theme_1",
            "name": "Theme Name",
            "color": "#3b82f6",
            "summary": "one-line summary",
            "arguments": [
              {
                "claim": "argument claim text",
                "evidence": [
                  {"type": "quote", "text": "short text", "timestamp": "MM:SS"},
                  {"type": "data_point", "text": "data point text", "timestamp": "MM:SS"}
                ]
              }
            ]
          }
        ],
        "cross_links": [
          {"source": "theme_1.0", "target": "theme_4.0", "relation": "supports"}
        ]
      }
    }

If map_data is missing, the script falls back to transforming the ``segments``
array using the legacy knowledge.json transformation path.
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
#   - Colours are tested against WCAG AA for large text (>=18px / bold >=14px)
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


def load_json(filepath: str) -> dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        filepath: Path to the JSON file.

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
    """Extract and normalise metadata fields from a knowledge.json-like dict.

    Handles flexible input shapes:
        - ``guest`` may be a plain string or ``{"name": "..."}``.
        - ``duration`` may be a string like ``"3h 47m"`` or
          ``{"total_seconds": 13620}``.

    Args:
        raw: The full parsed knowledge.json dict (expected to have a
            ``metadata`` key), or a dict that may contain ``meta`` at the
            top level (from visual_content.json).

    Returns:
        A dict with keys ``title``, ``guest``, ``date``, ``duration``.
        All values are plain strings. Missing metadata yields sensible
        defaults rather than raising.
    """
    # Support both knowledge.json "metadata" and visual_content.json "meta"
    meta: dict[str, Any] = raw.get("metadata", {}) or raw.get("meta", {})

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

    # Also check visual_content.json style: meta.stats.duration_formatted
    if not duration:
        vc_meta = raw.get("meta", {})
        if isinstance(vc_meta, dict):
            stats = vc_meta.get("stats", {})
            if isinstance(stats, dict):
                df = stats.get("duration_formatted", "")
                if df:
                    duration = str(df)

    return {
        "title": title,
        "guest": guest,
        "date": date,
        "duration": duration,
    }


def _merge_metadata(
    vc_meta: dict[str, str],
    knowledge_meta: Optional[dict[str, str]],
) -> dict[str, str]:
    """Merge metadata from visual_content.json with knowledge.json overrides.

    knowledge.json metadata takes priority for all fields.  Values from
    visual_content.json are used as fallbacks.

    Args:
        vc_meta: Metadata extracted from visual_content.json.
        knowledge_meta: Metadata extracted from knowledge.json, or None.

    Returns:
        Merged metadata dict with keys ``title``, ``guest``, ``date``,
        ``duration``.
    """
    if knowledge_meta is None:
        return vc_meta

    merged: dict[str, str] = {}
    for key in ("title", "guest", "date", "duration"):
        k_val = knowledge_meta.get(key, "")
        merged[key] = k_val if k_val else vc_meta.get(key, "")
    return merged


# ---------------------------------------------------------------------------
# Time-range formatting (used by legacy segment transform)
# ---------------------------------------------------------------------------


def _format_time_range(segment: dict[str, Any]) -> str:
    """Format a segment's ``time_range`` into a display string.

    Expects ``{"start": "HH:MM:SS", "end": "HH:MM:SS"}``.
    Returns ``"HH:MM:SS-HH:MM:SS"`` when both are present, otherwise just
    the start timestamp or an empty string.

    Args:
        segment: A segment dict from knowledge.json or visual_content.json.

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
# Helper: normalise cross-link source/target from theme_id.index to
#         topic_index.insight_index
# ---------------------------------------------------------------------------


def _normalise_cross_link_index(
    raw_index: str,
    theme_id_to_topic_idx: dict[str, int],
) -> str:
    """Convert a cross-link reference like ``"theme_1.0"`` to ``"0.0"``.

    Args:
        raw_index: A string of the form ``theme_N.insight_idx``.
        theme_id_to_topic_idx: Mapping from theme id (e.g. ``"theme_1"``)
            to the 0-based topic index.

    Returns:
        Normalised index string ``"topic.insight"``, or the original
        string if parsing fails.
    """
    if "." not in raw_index:
        return raw_index
    theme_id, _, insight_idx = raw_index.partition(".")
    topic_idx = theme_id_to_topic_idx.get(theme_id)
    if topic_idx is None:
        return raw_index
    return f"{topic_idx}.{insight_idx}"


# ---------------------------------------------------------------------------
# New: transform from visual_content.json map_data
# ---------------------------------------------------------------------------


def transform_from_map_data(
    vc_data: dict[str, Any],
    metadata: dict[str, str],
) -> dict[str, Any]:
    """Build the ``MINDMAP_DATA`` dict from visual_content.json's ``map_data``.

    Mapping rules:

    * ``map_data.central_thesis`` → top-level ``central_thesis``.
    * ``map_data.theme_nodes[]`` → ``topics[]`` (one per theme node).
        - ``name``, ``color``, ``summary`` map directly.
        - If a theme node has no color, a colour from ``COLOR_PALETTE`` is
          assigned in order.
    * Each ``theme_node.arguments[]`` → ``topic.insights[]``.
        - ``claim`` → ``insight.text``.
    * Each ``argument.evidence[]`` → ``insight.evidence[]``.
        - ``text``, ``timestamp``, ``type`` map directly.
    * ``map_data.cross_links[]`` → ``cross_links[]`` with normalised
      source/target indices.

    Args:
        vc_data: The full parsed visual_content.json dict.
        metadata: Pre-extracted metadata dict.

    Returns:
        A dict conforming to the ``MINDMAP_DATA`` schema.
    """
    map_data: dict[str, Any] = vc_data.get("map_data", {})
    theme_nodes: list[dict[str, Any]] = map_data.get("theme_nodes", [])

    # Build theme_id → topic_index mapping for cross-link normalisation
    theme_id_to_topic_idx: dict[str, int] = {}
    for idx, tn in enumerate(theme_nodes):
        tid = tn.get("id", "")
        if tid:
            theme_id_to_topic_idx[tid] = idx

    # Palette fallback tracker
    palette_offset: int = 0

    topics: list[dict[str, Any]] = []
    for tn in theme_nodes:
        color: str = tn.get("color", "")
        if not color:
            color = COLOR_PALETTE[palette_offset % len(COLOR_PALETTE)]
            palette_offset += 1

        insights: list[dict[str, Any]] = []
        for arg in tn.get("arguments", []):
            evidence_items: list[dict[str, str]] = []
            for ev in arg.get("evidence", []):
                evidence_items.append(
                    {
                        "text": ev.get("text", ""),
                        "timestamp": ev.get("timestamp", ""),
                        "type": ev.get("type", "quote"),
                        "full_text": ev.get("full_text", ""),
                    }
                )

            insights.append(
                {
                    "text": arg.get("claim", ""),
                    "evidence": evidence_items,
                    "importance": arg.get("importance", 3),
                    "explanation": arg.get("explanation", ""),
                    "insight_type": arg.get("insight_type", "claim"),
                }
            )

        # --- predictions (optional per-theme forward-looking items) ---
        predictions: list[dict[str, Any]] = []
        for pred in tn.get("predictions", []):
            predictions.append(
                {
                    "text": pred.get("text", ""),
                    "confidence": pred.get("confidence", "medium"),
                    "timeframe": pred.get("time_horizon", ""),
                }
            )

        topics.append(
            {
                "name": tn.get("name", ""),
                "color": color,
                "summary": tn.get("summary", ""),
                "insights": insights,
                "predictions": predictions,
            }
        )

    # Normalise cross-links
    raw_cross_links: list[dict[str, str]] = map_data.get("cross_links", [])
    cross_links: list[dict[str, str]] = []
    for cl in raw_cross_links:
        cross_links.append(
            {
                "source": _normalise_cross_link_index(
                    cl.get("source", ""), theme_id_to_topic_idx
                ),
                "target": _normalise_cross_link_index(
                    cl.get("target", ""), theme_id_to_topic_idx
                ),
                "relation": cl.get("relation", "supports"),
            }
        )

    result: dict[str, Any] = {
        "title": metadata["title"],
        "guest": metadata["guest"],
        "date": metadata["date"],
        "duration": metadata["duration"],
        "central_thesis": map_data.get("central_thesis", ""),
        "topics": topics,
        "cross_links": cross_links,
    }

    # Attach pipeline stats when present (theme_count, segment_count, etc.)
    stats = map_data.get("stats")
    if isinstance(stats, dict) and stats:
        result["stats"] = stats

    return result


# ---------------------------------------------------------------------------
# Legacy: transform from segments (knowledge.json fallback)
# ---------------------------------------------------------------------------


def transform_from_segments(
    raw: dict[str, Any],
    metadata: dict[str, str],
) -> dict[str, Any]:
    """Transform knowledge.json / visual_content.json segments into the
    ``MINDMAP_DATA`` format (legacy fallback path).

    Mapping rules:

    * ``segments`` → ``topics`` array (one topic per segment).
    * Each topic is assigned a distinct colour from ``COLOR_PALETTE``
      in round-robin order.
    * ``segment.insights`` → ``topic.insights[]`` (each with an empty
      ``evidence`` list for compatibility).
    * ``segment.golden_quotes`` → ``topic.quotes[]`` (``text``,
      ``timestamp``, ``speaker``).
    * ``segment.data_points`` → ``topic.data_points[]`` (``text``,
      ``timestamp``, ``type``).

    Args:
        raw: The full parsed JSON dict containing a ``segments`` key.
        metadata: Pre-extracted metadata dict.

    Returns:
        A dict conforming to the ``MINDMAP_DATA`` schema.
    """
    segments: list[dict[str, Any]] = raw.get("segments", [])

    topics: list[dict[str, Any]] = []
    for idx, seg in enumerate(segments):
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]

        # --- insights (with empty evidence for compatibility) ---
        insights: list[dict[str, Any]] = []
        for ins in seg.get("insights", []):
            insights.append(
                {
                    "text": ins.get("text", ""),
                    "timestamp": ins.get("timestamp", ""),
                    "evidence": [],
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

    result: dict[str, Any] = {
        "title": metadata["title"],
        "guest": metadata["guest"],
        "date": metadata["date"],
        "duration": metadata["duration"],
        "topics": topics,
    }

    return result


# ---------------------------------------------------------------------------
# Unified transform entry point
# ---------------------------------------------------------------------------


def transform_to_mindmap_data(
    vc_data: dict[str, Any],
    metadata: dict[str, str],
) -> dict[str, Any]:
    """Build ``MINDMAP_DATA`` from visual_content.json, falling back to the
    legacy segment-based transformation when ``map_data`` is absent.

    Args:
        vc_data: The full parsed visual_content.json dict.
        metadata: Merged metadata dict (from knowledge.json + VC meta).

    Returns:
        A dict conforming to the ``MINDMAP_DATA`` schema.
    """
    map_data = vc_data.get("map_data")
    if map_data and isinstance(map_data, dict) and map_data.get("theme_nodes"):
        return transform_from_map_data(vc_data, metadata)

    # Fall back to segment-based transformation
    return transform_from_segments(vc_data, metadata)


# ---------------------------------------------------------------------------
# JavaScript rendering
# ---------------------------------------------------------------------------


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
    3. **Existing declaration** — locate ``const MINDMAP_DATA = ...;`` via
       brace-depth tracking and replace the whole block.

    Args:
        template: The HTML template string.
        mindmap_data_js: The ``const MINDMAP_DATA = ...;`` string to insert.

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
    """Replace the ``const MINDMAP_DATA = {...};`` block inside *template*.

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
            "from a visual_content.json file produced by the interview "
            "analysis pipeline. Uses the map_data field for the mindmap "
            "structure, with optional knowledge.json for metadata."
        ),
    )
    parser.add_argument(
        "visual_content_json",
        metavar="VISUAL_CONTENT_JSON",
        help="Path to the visual_content.json input file (primary data source).",
    )
    parser.add_argument(
        "--knowledge-json",
        "-k",
        metavar="PATH",
        default=None,
        help=(
            "Path to a knowledge.json file for metadata "
            "(title, guest, date, duration). "
            "Metadata is also extracted from visual_content.json as a fallback."
        ),
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

    # ---- 2. Load visual_content.json --------------------------------------
    try:
        vc_data = load_json(args.visual_content_json)
    except FileNotFoundError:
        print(
            f"Error: file not found: {args.visual_content_json}",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(
            f"Error: invalid JSON in {args.visual_content_json}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as exc:
        print(
            f"Error: failed to read {args.visual_content_json}: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    # ---- 3. Load knowledge.json (optional, for metadata) ------------------
    knowledge_meta: Optional[dict[str, str]] = None
    if args.knowledge_json:
        try:
            knowledge_data = load_json(args.knowledge_json)
            knowledge_meta = _extract_metadata(knowledge_data)
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

    # ---- 4. Extract / merge metadata --------------------------------------
    vc_meta = _extract_metadata(vc_data)
    metadata = _merge_metadata(vc_meta, knowledge_meta)

    # ---- 5. Load template -------------------------------------------------
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

    # ---- 6. Transform data into MINDMAP_DATA format -----------------------
    try:
        mindmap_data = transform_to_mindmap_data(vc_data, metadata)
    except Exception as exc:
        print(
            f"Error: failed to transform visual content data: {exc}",
            file=sys.stderr,
        )
        sys.exit(3)

    # ---- 7. Render JavaScript variable ------------------------------------
    mindmap_data_js = format_mindmap_data_js(mindmap_data)

    # ---- 8. Embed into template -------------------------------------------
    try:
        html_output = embed_data(template, mindmap_data_js)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(4)

    # ---- 9. Write output --------------------------------------------------
    try:
        write_output(args.output, html_output)
    except OSError as exc:
        print(
            f"Error: failed to write {args.output}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    # ---- 10. Summary ------------------------------------------------------
    topic_count = len(mindmap_data.get("topics", []))
    total_insights = 0
    total_evidence = 0
    for t in mindmap_data.get("topics", []):
        for ins in t.get("insights", []):
            total_insights += 1
            total_evidence += len(ins.get("evidence", []))
    total_quotes = sum(
        len(t.get("quotes", [])) for t in mindmap_data.get("topics", [])
    )
    total_data_points = sum(
        len(t.get("data_points", [])) for t in mindmap_data.get("topics", [])
    )
    cross_link_count = len(mindmap_data.get("cross_links", []))
    central_thesis = mindmap_data.get("central_thesis", "")

    used_map_data = "map_data" if central_thesis else "segments (legacy fallback)"
    parts: list[str] = [
        f"已生成 {args.output}  "
        f"({topic_count} 个主题, "
        f"{total_insights} 个论点",
    ]
    if total_evidence:
        parts.append(
            f"{total_evidence} 条证据"
        )
    if total_quotes:
        parts.append(
            f"{total_quotes} 条引文"
        )
    if total_data_points:
        parts.append(
            f"{total_data_points} 个数据点"
        )
    if cross_link_count:
        parts.append(
            f"{cross_link_count} 条交叉连线"
        )
    parts.append(f"数据源: {used_map_data})")
    print("  ".join(parts))


if __name__ == "__main__":
    main()
