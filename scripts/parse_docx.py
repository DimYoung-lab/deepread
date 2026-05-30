#!/usr/bin/env python3
"""Extract structured interview turns from .docx transcript files.

Parses .docx transcripts with alternating speaker labels, timestamps,
and multi-paragraph turns into clean JSON with metadata and normalized turns.

Typical transcript format:
    Paragraph 1: title line
    Paragraph 2: date line
    Paragraph 3: empty
    Paragraph 4: "发言人1  00:08"
    Paragraph 5: "Hello大家好，我是..."
    Paragraph 6: empty
    Paragraph 7: "发言人2  00:45"
    Paragraph 8: "response text..."
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Optional

from docx import Document


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Person:
    name: str
    affiliation: str = ""


@dataclass
class Metadata:
    title: str = ""
    date: str = ""
    guest: Optional[Person] = None
    interviewer: Optional[Person] = None
    total_duration_seconds: int = 0
    total_turns: int = 0
    language: str = "zh"


@dataclass
class Turn:
    index: int
    speaker: str  # "guest" | "interviewer" | "speaker" | "speaker_1" | ...
    speaker_label: str
    timestamp_raw: str
    timestamp_seconds: int
    text: str


@dataclass
class Transcript:
    metadata: Metadata
    turns: list[Turn] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Timestamp parsing
# ---------------------------------------------------------------------------

_TIMESTAMP_RE = re.compile(
    r"(?:(\d{1,2}):)?(\d{1,2}):(\d{2})"
)


def parse_timestamp(raw: str) -> int:
    """Normalize a timestamp string to total seconds (int).

    Supports two formats:
        MM:SS       → seconds
        HH:MM:SS    → seconds

    Raises ValueError if the string cannot be parsed.
    """
    raw = raw.strip()
    m = _TIMESTAMP_RE.fullmatch(raw)
    if not m:
        raise ValueError(f"Cannot parse timestamp: {raw!r}")

    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2))
    seconds = int(m.group(3))

    return hours * 3600 + minutes * 60 + seconds


# ---------------------------------------------------------------------------
# Speaker label / turn detection
# ---------------------------------------------------------------------------

# A paragraph whose trimmed text looks like "发言人1  00:08" or "SpeakerA  12:34"
_SPEAKER_LINE_RE = re.compile(
    r"^(.+?)\s{2,}(\d{1,2}:\d{2}(?::\d{2})?)$"
)


def _looks_like_date(text: str) -> bool:
    """Heuristic: detect date strings like 2024-01-15, 2024年1月15日, etc."""
    text = text.strip()
    return bool(
        re.match(r"^\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?$", text)
        or re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$", text)
        or re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$", text)
    )


def _is_empty_paragraph(para) -> bool:
    """Return True if the docx paragraph has no meaningful text."""
    text = para.text.strip() if para.text else ""
    return len(text) == 0


def _get_paragraphs(doc: Document) -> list[dict]:
    """Extract paragraph data from a python-docx Document.

    Returns list of dicts with 'text' and 'is_empty' keys.
    """
    result: list[dict] = []
    for para in doc.paragraphs:
        text = para.text.strip() if para.text else ""
        result.append({"text": text, "is_empty": len(text) == 0})
    return result


# ---------------------------------------------------------------------------
# Core parsing
# ---------------------------------------------------------------------------


def parse_transcript(
    filepath: str, num_speakers: Optional[int] = None, language: str = "zh"
) -> Transcript:
    """Parse a .docx interview transcript into a Transcript object.

    Args:
        filepath: Path to the .docx file.
        num_speakers: Explicit speaker count for role labeling.
            None (default) auto-detects from the data.
        language: Language code for the transcript metadata (default 'zh').

    Returns:
        Transcript with parsed metadata and turns.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the document format is unrecognised.
    """
    try:
        doc = Document(filepath)
    except FileNotFoundError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to open {filepath}: {exc}") from exc

    paragraphs = _get_paragraphs(doc)
    if not paragraphs:
        raise ValueError("Document contains no paragraphs.")

    # --- Phase 1: extract header metadata ---
    header_paragraphs: list[str] = []
    body_start_idx = 0

    for i, p in enumerate(paragraphs):
        if p["is_empty"]:
            # First empty paragraph marks end of header
            header_paragraphs = [pp["text"] for pp in paragraphs[:i] if not pp["is_empty"]]
            body_start_idx = i + 1
            break

    if body_start_idx == 0:
        # No empty separator found — treat the whole document as body
        header_paragraphs = []
        body_start_idx = 0

    metadata = _extract_metadata(header_paragraphs)
    metadata.language = language

    # --- Phase 2: parse speaker turns from body ---
    raw_turns = _parse_raw_turns(paragraphs[body_start_idx:])
    if not raw_turns:
        raise ValueError("No speaker turns found in document body.")

    # --- Phase 3: auto-detect speaker roles ---
    speaker_map = _detect_speaker_roles(raw_turns, num_speakers)

    # --- Phase 4: build Turn objects ---
    turns: list[Turn] = []
    for idx, rt in enumerate(raw_turns, start=1):
        speaker_role = speaker_map.get(rt["label"], "unknown")
        ts_seconds = parse_timestamp(rt["timestamp"])
        turns.append(
            Turn(
                index=idx,
                speaker=speaker_role,
                speaker_label=rt["label"],
                timestamp_raw=rt["timestamp"],
                timestamp_seconds=ts_seconds,
                text=rt["text"],
            )
        )

    # --- Phase 5: compute metadata ---
    metadata.total_turns = len(turns)
    if turns:
        metadata.total_duration_seconds = turns[-1].timestamp_seconds

    # Attempt to name the guest / interviewer if the label is obvious
    for label, role in speaker_map.items():
        if role == "guest" and metadata.guest is None:
            metadata.guest = Person(name=label)
        elif role == "interviewer" and metadata.interviewer is None:
            metadata.interviewer = Person(name=label)

    return Transcript(metadata=metadata, turns=turns)


def _extract_metadata(header_texts: list[str]) -> Metadata:
    """Extract Metadata from the list of header paragraph strings."""
    meta = Metadata()

    if not header_texts:
        return meta

    # First non-empty line is the title
    meta.title = header_texts[0].strip()

    # Look for a date among remaining lines
    for text in header_texts[1:]:
        if _looks_like_date(text):
            meta.date = text.strip()
            break

    return meta


def _parse_raw_turns(body_paragraphs: list[dict]) -> list[dict]:
    """Parse raw turns from body paragraphs.

    A "raw turn" is a dict with keys: 'label', 'timestamp', 'text'.

    Multi-paragraph turns (a speaker continuing across consecutive paragraphs
    without a new speaker label) are merged.
    """
    raw_turns: list[dict] = []
    current_turn: Optional[dict] = None

    for p in body_paragraphs:
        text = p["text"]

        # Skip truly empty paragraphs between turns
        if p["is_empty"]:
            if current_turn is not None:
                # End of current multi-paragraph turn
                raw_turns.append(current_turn)
                current_turn = None
            continue

        # Check if this paragraph starts a new turn (speaker + timestamp)
        m = _SPEAKER_LINE_RE.match(text)
        if m:
            # Save previous turn if any
            if current_turn is not None:
                raw_turns.append(current_turn)

            label = m.group(1).strip()
            timestamp_raw = m.group(2).strip()
            # The text after the timestamp is on the same line
            rest = text[m.end():].strip()
            current_turn = {"label": label, "timestamp": timestamp_raw, "text": rest}
        else:
            # Continuation of current speaker's turn
            if current_turn is not None:
                if current_turn["text"]:
                    current_turn["text"] += "\n\n" + text
                else:
                    current_turn["text"] = text
            # If current_turn is None and we see text, it might be a
            # header-like paragraph in the body — skip it.

    # Don't forget the last turn
    if current_turn is not None:
        raw_turns.append(current_turn)

    return raw_turns


def _detect_speaker_roles(
    raw_turns: list[dict], num_speakers: Optional[int] = None
) -> dict[str, str]:
    """Auto-detect speaker roles from raw turns.

    Heuristic for auto-detection (when num_speakers is None):
    - The most active speaker comes first; ties are broken by total text length.

    Labeling scheme:
    - 1 speaker  → "speaker" (monologue / lecture)
    - 2 speakers → "guest" + "interviewer" (Q&A, existing behaviour)
    - 3+ speakers → "speaker_1", "speaker_2", ... (panel / debate)

    Args:
        raw_turns: List of raw turn dicts with 'label', 'timestamp', 'text'.
        num_speakers: Explicit speaker count for the labeling scheme.
            None (default) means auto-detect from the data.

    Returns:
        Dict mapping raw speaker label → role name.
    """
    speakers: dict[str, dict] = {}
    for rt in raw_turns:
        label = rt["label"]
        if label not in speakers:
            speakers[label] = {"count": 0, "total_chars": 0}
        speakers[label]["count"] += 1
        speakers[label]["total_chars"] += len(rt["text"])

    # Sort by count descending, then by total_chars descending
    sorted_labels = [
        label
        for label, _ in sorted(
            speakers.items(),
            key=lambda kv: (kv[1]["count"], kv[1]["total_chars"]),
            reverse=True,
        )
    ]

    n = len(sorted_labels)
    if n == 0:
        return {}

    # Determine labeling scheme
    count = num_speakers if num_speakers is not None else n

    if count <= 1:
        # Monologue / lecture
        return {label: "speaker" for label in sorted_labels}
    elif count == 2:
        # Q&A: most-active speaker is guest, second is interviewer
        result: dict[str, str] = {}
        if n >= 1:
            result[sorted_labels[0]] = "guest"
        if n >= 2:
            result[sorted_labels[1]] = "interviewer"
        # Any additional speakers beyond 2 get numbered
        for i in range(2, n):
            result[sorted_labels[i]] = f"speaker_{i + 1}"
        return result
    else:
        # Panel / debate
        return {label: f"speaker_{i + 1}" for i, label in enumerate(sorted_labels)}


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def transcript_to_dict(transcript: Transcript) -> dict:
    """Convert Transcript to a JSON-serialisable dict."""
    meta = transcript.metadata
    turns_out: list[dict] = []

    for turn in transcript.turns:
        turns_out.append(
            {
                "index": turn.index,
                "speaker": turn.speaker,
                "speaker_label": turn.speaker_label,
                "timestamp_raw": turn.timestamp_raw,
                "timestamp_seconds": turn.timestamp_seconds,
                "text": turn.text,
            }
        )

    return {
        "metadata": {
            "title": meta.title,
            "date": meta.date,
            "guest": {
                "name": meta.guest.name if meta.guest else "",
                "affiliation": meta.guest.affiliation if meta.guest else "",
            },
            "interviewer": {
                "name": meta.interviewer.name if meta.interviewer else "",
            },
            "total_duration_seconds": meta.total_duration_seconds,
            "total_turns": meta.total_turns,
            "language": meta.language,
        },
        "turns": turns_out,
    }


def output_json(transcript: Transcript, raw: bool = False) -> str:
    """Produce JSON string from a Transcript.

    Args:
        transcript: Parsed transcript.
        raw: If True, include raw paragraph-level data as well.

    Returns:
        JSON string (UTF-8).
    """
    result = transcript_to_dict(transcript)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract structured interview turns from a .docx transcript.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to the .docx transcript file.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Include raw paragraph-level metadata in output.",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        default=None,
        help="Write JSON to PATH instead of stdout.",
    )
    parser.add_argument(
        "--speakers",
        type=int,
        metavar="N",
        default=None,
        help="Number of speakers (1=monologue, 2=Q&A, 3+=panel). "
        "Default: auto-detect from transcript data.",
    )
    parser.add_argument(
        "--language",
        metavar="CODE",
        default="zh",
        help="Language code for transcript metadata (default: zh).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_argparser()
    args = parser.parse_args(argv)

    try:
        transcript = parse_transcript(
            args.input, num_speakers=args.speakers, language=args.language
        )
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(2)

    json_str = output_json(transcript, raw=args.raw)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(json_str)
                fh.write("\n")
        except OSError as exc:
            print(f"Error writing {args.output}: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
