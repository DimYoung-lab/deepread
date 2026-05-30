#!/usr/bin/env python3
"""Stage 1.5: Transcript Validation — apply glossary-based corrections to turns.json.

Reads a glossary markdown file and uses it to correct transcription errors in
interview turns. Outputs a corrected turns file and a corrections audit log.

Usage:
    python validate_transcript.py turns.json \\
        --glossary references/transcript-glossary.md \\
        --output turns-corrected.json

    python validate_transcript.py turns.json \\
        --glossary references/transcript-glossary.md \\
        --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Glossary parser
# ---------------------------------------------------------------------------

# Expected glossary markdown format:
#   | variant | canonical | entity_type | notes |
#   |---------|-----------|-------------|-------|
#   | C-Dance | Seedance  | product     | ...   |
#
# Also supports plain heading + list format:
#   ## Products
#   - **Seedance** (variants: C-Dance, C Dance, c-dance)
#   - **Anthropic** (variants: anthopic, thopic, authority c)


def parse_glossary_table(lines: List[str], start: int) -> Tuple[Dict[str, str], Dict[str, str], int]:
    """Parse a markdown table section into {variant: canonical} and {canonical: entity_type} maps.

    Returns (correction_map, type_map, next_line_index).
    """
    correction_map: Dict[str, str] = {}
    type_map: Dict[str, str] = {}

    # Find the header row
    header_idx = start
    while header_idx < len(lines) and "|" not in lines[header_idx]:
        header_idx += 1
    if header_idx >= len(lines):
        return correction_map, type_map, header_idx

    # Parse header to find column positions
    header = [c.strip().lower() for c in lines[header_idx].split("|") if c.strip()]
    variant_col = next((i for i, h in enumerate(header) if "variant" in h), 0)
    canonical_col = next((i for i, h in enumerate(header) if "canonical" in h), 1)
    type_col = next((i for i, h in enumerate(header) if "type" in h or "entity" in h), 2)

    # Skip separator line
    i = header_idx + 1
    while i < len(lines) and ("---" in lines[i] or "|" not in lines[i]):
        i += 1
        if i >= len(lines):
            return correction_map, type_map, i

    # Parse data rows
    while i < len(lines):
        line = lines[i].strip()
        if not line or not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|") if c.strip() != ""]
        if len(cells) <= max(variant_col, canonical_col):
            i += 1
            continue

        variant = cells[variant_col] if variant_col < len(cells) else ""
        canonical = cells[canonical_col] if canonical_col < len(cells) else ""
        entity_type = cells[type_col] if type_col < len(cells) else "unknown"

        if variant and canonical:
            correction_map[variant] = canonical
            type_map[canonical] = entity_type

        i += 1

    return correction_map, type_map, i


def parse_glossary_list(lines: List[str], start: int) -> Tuple[Dict[str, str], Dict[str, str], int]:
    """Parse a heading + list style glossary section.

    Format:
        ## Category Name
        - **Canonical** (variants: var1, var2, var3)
        - **Canonical2** (variants: varA, varB)
    """
    correction_map: Dict[str, str] = {}
    type_map: Dict[str, str] = {}
    current_type = "unknown"

    i = start
    while i < len(lines):
        line = lines[i].strip()

        # Heading sets the entity type category
        if line.startswith("## "):
            current_type = line[3:].strip().lower()
            if current_type.endswith("s"):
                current_type = current_type[:-1]
            i += 1
            continue
        if line.startswith("# "):
            current_type = line[2:].strip().lower()
            if current_type.endswith("s"):
                current_type = current_type[:-1]
            i += 1
            continue

        # List item: **Canonical** (variants: var1, var2)
        if line.startswith("- ") or line.startswith("* "):
            content = line[2:].strip()
            match = re.match(
                r"\*\*(.+?)\*\*\s*\((?:variants?|also|aka)[:\s]*(.+?)\)",
                content,
            )
            if match:
                canonical = match.group(1).strip()
                variants_str = match.group(2).strip()
                # Split by comma or semicolon
                for variant in re.split(r"[,;]\s*", variants_str):
                    variant = variant.strip().strip('"').strip("'")
                    if variant:
                        correction_map[variant] = canonical
                        type_map[canonical] = current_type
            else:
                # Simple **Canonical** without explicit variants
                bold_match = re.match(r"\*\*(.+?)\*\*", content)
                if bold_match:
                    canonical = bold_match.group(1).strip()
                    # The canonical form corrects its own case variants
                    correction_map[canonical.lower()] = canonical
                    type_map[canonical] = current_type

        i += 1

    return correction_map, type_map, i


def parse_glossary_detail(text: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Parse ### Heading + key-value bullet glossary format using regex.

    Format:
        ### EntityName
        - **Category**: company
        - **Canonical**: DeepMind
        - **Variants**: var1, var2, var3
    """
    correction_map: Dict[str, str] = {}
    type_map: Dict[str, str] = {}

    # Match each entity block: ### Name followed by its bullet points
    entity_pattern = re.compile(
        r'###\s+(.+?)\n(.*?)(?=\n###\s|\n##\s|\n---\s|\Z)',
        re.DOTALL,
    )

    for match in entity_pattern.finditer(text):
        entity_name = match.group(1).strip()
        body = match.group(2)

        # Extract canonical form
        canonical_match = re.search(r'\*\*Canonical\*\*\s*:\s*(.+)', body)
        canonical = canonical_match.group(1).strip() if canonical_match else entity_name

        # Extract category
        cat_match = re.search(r'\*\*Category\*\*\s*:\s*(.+)', body)
        category = cat_match.group(1).strip().lower() if cat_match else "unknown"

        # Extract variants
        variants_match = re.search(r'\*\*(?:Variants?|variant)\*\*\s*:\s*(.+)', body)
        if variants_match:
            variants_str = variants_match.group(1).strip()
            for v in re.split(r'[,;，；]\s*', variants_str):
                v = v.strip().strip('"').strip("'")
                if v and v != canonical:
                    correction_map[v] = canonical

        type_map[canonical] = category

    return correction_map, type_map


def parse_glossary(filepath: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Parse a glossary markdown file into a correction map and type map.

    Returns:
        correction_map: Dict[variant, canonical]  e.g. {"C-Dance": "Seedance"}
        type_map:       Dict[canonical, entity_type]  e.g. {"Seedance": "product"}
    """
    path = Path(filepath)
    if not path.exists():
        print(f"Warning: glossary file not found: {filepath}", file=sys.stderr)
        return {}, {}

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    correction_map: Dict[str, str] = {}
    type_map: Dict[str, str] = {}

    # Try ### detail format first (most common)
    detail_map, detail_types = parse_glossary_detail(text)
    if detail_map:
        correction_map.update(detail_map)
        type_map.update(detail_types)

    # Fall back to line-by-line parsers for other formats
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect table sections
        if line.startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            table_map, table_types, next_i = parse_glossary_table(lines, i)
            correction_map.update(table_map)
            type_map.update(table_types)
            i = max(next_i, i + 1)
            continue

        # Detect list-based sections (## headings)
        if line.startswith("## ") and not line.startswith("### "):
            if i + 1 < len(lines) and (
                lines[i + 1].strip().startswith("- ")
                or lines[i + 1].strip().startswith("* ")
            ):
                list_map, list_types, next_i = parse_glossary_list(lines, i)
                correction_map.update(list_map)
                type_map.update(list_types)
                i = next_i
                continue

        i += 1

    return correction_map, type_map


# ---------------------------------------------------------------------------
# Text correction engine
# ---------------------------------------------------------------------------


def build_case_insensitive_map(
    correction_map: Dict[str, str],
) -> Dict[str, Tuple[str, str]]:
    """Build a lowercased lookup that preserves the original variant and canonical.

    Returns {lower_variant: (original_variant, canonical)}.
    """
    ci_map: Dict[str, Tuple[str, str]] = {}
    for variant, canonical in correction_map.items():
        lower = variant.lower()
        # If there's a conflict, prefer the longer variant (more specific)
        if lower not in ci_map or len(variant) > len(ci_map[lower][0]):
            ci_map[lower] = (variant, canonical)
    return ci_map


def is_chinese_char(ch: str) -> bool:
    """Check if a character is a CJK unified ideograph."""
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x20000 <= cp <= 0x2A6DF
    )


def is_english_word(text: str) -> bool:
    """Return True if the text is predominantly Latin script (not Chinese)."""
    if not text:
        return False
    latin = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    cjk = sum(1 for ch in text if is_chinese_char(ch))
    return latin > cjk


def apply_corrections(
    text: str,
    correction_map: Dict[str, str],
    ci_map: Dict[str, Tuple[str, str]],
    skip_fuzzy: bool = False,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Apply glossary corrections to a single turn's text.

    Strategy:
        - Chinese character sequences: direct substring replacement (longest first)
        - English terms: case-insensitive regex with word boundaries (longest first)
        - Both approaches are order-preserving — longest variants matched first to
          prevent partial matches from consuming shorter matches incorrectly.

    Returns (corrected_text, list_of_correction_records).
    """
    corrections: List[Dict[str, Any]] = []
    corrected = text

    # Separate Chinese vs English variants for different matching strategies.
    zh_variants: List[Tuple[str, str]] = []
    en_variants: List[Tuple[str, str]] = []

    for variant, canonical in correction_map.items():
        if any(is_chinese_char(ch) for ch in variant):
            zh_variants.append((variant, canonical))
        elif any(ch.isascii() and ch.isalpha() for ch in variant):
            en_variants.append((variant, canonical))
        else:
            # Punctuation-heavy or ambiguous — try direct replacement
            zh_variants.append((variant, canonical))

    # Sort by length descending so longer (more specific) variants match first.
    zh_variants.sort(key=lambda x: -len(x[0]))
    en_variants.sort(key=lambda x: -len(x[0]))

    # --- Phase 1: Chinese character sequence replacement ---
    # Direct substring replacement; order handled by longest-first sort.
    for variant, canonical in zh_variants:
        count = corrected.count(variant)
        if count > 0:
            corrected = corrected.replace(variant, canonical)
            corrections.append(
                {
                    "original_fragment": variant,
                    "corrected": canonical,
                    "entity_type": "unknown",  # populated later
                    "confidence": "high",
                }
            )

    # --- Phase 2: English term case-insensitive regex replacement ---
    for variant, canonical in en_variants:
        # Escape the variant for regex but allow case-insensitive matching
        pattern = re.compile(
            r"(?<![a-zA-Z])" + re.escape(variant) + r"(?![a-zA-Z])",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(corrected))
        if matches:
            # Build a new string with replacements (reverse order to preserve
            # indices, or just use sub)
            corrected = pattern.sub(canonical, corrected)

            for _ in matches:
                corrections.append(
                    {
                        "original_fragment": variant,
                        "corrected": canonical,
                        "entity_type": "unknown",
                        "confidence": "high",
                    }
                )

    # --- Phase 3: Fuzzy matching for potential new variants ---
    # For each canonical term, check if a "close but not exact" variant exists.
    if skip_fuzzy:
        fuzzy_corrections = []
    else:
        fuzzy_corrections = _fuzzy_match(corrected, ci_map, correction_map)
    for fc in fuzzy_corrections:
        if fc["original_fragment"] not in [
            c["original_fragment"] for c in corrections
        ]:
            # Attempt to replace the fuzzy fragment with canonical
            fragment = fc["original_fragment"]
            canonical = fc["corrected"]
            if fragment in corrected:
                corrected = corrected.replace(fragment, canonical)
                fc["confidence"] = "medium"
            else:
                # Could not replace directly — mark as low-confidence detection
                fc["confidence"] = "low"
            corrections.append(fc)

    return corrected, corrections


def _fuzzy_match(
    text: str,
    ci_map: Dict[str, Tuple[str, str]],
    correction_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Detect potential new variants via fuzzy pattern matching.

    Strategy:
        - For English canonicals, look for similar substrings within edit
          distance of 2 (e.g., missing/extra characters).
        - For Chinese canonicals, look for partial character overlaps.
    """
    fuzzy: List[Dict[str, Any]] = []

    # Collect unique canonicals
    canonicals: Dict[str, str] = {}
    for variant, canonical in correction_map.items():
        canonicals[canonical] = variant  # keep one sample variant

    for canonical, sample_variant in canonicals.items():
        if is_english_word(canonical):
            # Build a "flexible" regex: allow up to 1-2 char insertions/deletions
            # between characters of the canonical.
            fuzzy_found = _fuzzy_english_search(text, canonical, sample_variant)
            fuzzy.extend(fuzzy_found)
        else:
            fuzzy_found = _fuzzy_chinese_search(text, canonical, sample_variant)
            fuzzy.extend(fuzzy_found)

    return fuzzy


def _fuzzy_english_search(
    text: str,
    canonical: str,
    sample_variant: str,
) -> List[Dict[str, Any]]:
    """Search for fuzzy English matches — missing/spurious characters."""
    results: List[Dict[str, Any]] = []
    canonical_lower = canonical.lower()

    # Build a regex that allows minor variations:
    # Split canonical into tokens and allow optional separators or slight edits.
    if len(canonical) < 4:
        return results  # too short for meaningful fuzzy matching

    # Pattern: look for known prefix + fuzzy middle
    # e.g., "anthopic" vs "Anthropic" — missing 'r' after 'th'
    # Build the pattern by inserting optional characters between each pair.
    chars = list(canonical_lower)
    # Allow one optional extra character or missing character
    fuzzy_pattern_parts = []
    for i, ch in enumerate(chars):
        fuzzy_pattern_parts.append(re.escape(ch))
        if i < len(chars) - 1:
            # Allow 0-1 extra characters between each pair
            fuzzy_pattern_parts.append(r"[a-z]?")
    fuzzy_regex = "".join(fuzzy_pattern_parts)

    pattern = re.compile(r"(?<![a-zA-Z])(" + fuzzy_regex + r")(?![a-zA-Z])", re.IGNORECASE)
    for match in pattern.finditer(text):
        matched = match.group(1)
        matched_lower = matched.lower()
        if matched_lower == canonical_lower:
            # Exact match — skip, Phase 2 already handled it
            continue
        if matched_lower == sample_variant.lower():
            # Already in correction map
            continue
        # Check edit distance confirmation
        if _edit_distance(matched_lower, canonical_lower) <= 2:
            results.append(
                {
                    "original_fragment": matched,
                    "corrected": canonical,
                    "entity_type": "unknown",
                    "confidence": "medium",
                }
            )

    return results


def _fuzzy_chinese_search(
    text: str,
    canonical: str,
    sample_variant: str,
) -> List[Dict[str, Any]]:
    """Search for fuzzy Chinese matches — character-level partial overlaps."""
    results: List[Dict[str, Any]] = []
    if len(canonical) < 2:
        return results
    if canonical in text:
        return results  # already exact, no fuzzy needed

    # Check if 70%+ of characters from canonical appear in close proximity
    for i in range(len(text) - 1):
        window_end = min(i + len(canonical) + 2, len(text))
        window = text[i:window_end]
        overlap = sum(1 for ch in canonical if ch in window)
        ratio = overlap / len(canonical)
        if ratio >= 0.7 and window != canonical:
            results.append(
                {
                    "original_fragment": window,
                    "corrected": canonical,
                    "entity_type": "unknown",
                    "confidence": "low",
                }
            )
            break  # one fuzzy match per canonical per text

    return results


def _edit_distance(s1: str, s2: str) -> int:
    """Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insert = prev[j + 1] + 1
            delete = curr[j] + 1
            substitute = prev[j] + (0 if c1 == c2 else 1)
            curr.append(min(insert, delete, substitute))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------


@dataclass
class CorrectionEntry:
    turn_index: int
    original_fragment: str
    corrected: str
    entity_type: str
    confidence: str


def load_turns(filepath: str) -> Dict[str, Any]:
    """Load turns.json and return the full document."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def process_turns(
    data: Dict[str, Any],
    correction_map: Dict[str, str],
    type_map: Dict[str, str],
    dry_run: bool = False,
    skip_fuzzy: bool = False,
) -> Tuple[List[CorrectionEntry], Dict[str, Any]]:
    """Process all turns, applying glossary corrections.

    Returns (corrections_list, output_data_or_none).
    When dry_run is True, output_data is None.
    """
    ci_map = build_case_insensitive_map(correction_map)
    all_corrections: List[CorrectionEntry] = []
    corrected_data = json.loads(json.dumps(data))  # deep copy

    turns = corrected_data.get("turns", [])
    for turn in turns:
        idx = turn.get("index", -1)
        original_text = turn.get("text", "")

        corrected_text, corrections = apply_corrections(
            original_text, correction_map, ci_map, skip_fuzzy=skip_fuzzy
        )

        # Enrich corrections with entity_type and turn_index
        for c in corrections:
            canonical = c["corrected"]
            c["entity_type"] = type_map.get(canonical, "unknown")
            all_corrections.append(
                CorrectionEntry(
                    turn_index=idx,
                    original_fragment=c["original_fragment"],
                    corrected=c["corrected"],
                    entity_type=c["entity_type"],
                    confidence=c["confidence"],
                )
            )

        # Update turn text and add corrections_applied count
        if corrections:
            if not dry_run:
                turn["text"] = corrected_text
            turn["corrections_applied"] = len(corrections)

    if dry_run:
        return all_corrections, {}
    return all_corrections, corrected_data


def build_summary(
    corrections: List[CorrectionEntry],
    type_map: Dict[str, str],
) -> Dict[str, Any]:
    """Generate a summary report of corrections by category."""
    by_type: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "confidence": {"high": 0, "medium": 0, "low": 0}, "examples": []}
    )
    by_confidence: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    seen_examples: set = set()

    for ce in corrections:
        etype = ce.entity_type or "unknown"
        stats = by_type[etype]
        stats["count"] += 1
        stats["confidence"][ce.confidence] += 1
        by_confidence[ce.confidence] += 1

        # Collect up to 3 examples per type
        key = (etype, ce.original_fragment, ce.corrected)
        if key not in seen_examples and len(stats["examples"]) < 3:
            seen_examples.add(key)
            stats["examples"].append(
                {"variant": ce.original_fragment, "canonical": ce.corrected}
            )

    return {
        "total_corrections": len(corrections),
        "turns_affected": len(set(ce.turn_index for ce in corrections)),
        "by_confidence": by_confidence,
        "by_type": {
            etype: {
                "count": s["count"],
                "confidence": s["confidence"],
                "examples": s["examples"],
            }
            for etype, s in sorted(by_type.items(), key=lambda x: -x[1]["count"])
        },
    }


def output_corrections_json(
    corrections: List[CorrectionEntry],
    filepath: str,
) -> None:
    """Write corrections.json to disk."""
    records = [asdict(ce) for ce in corrections]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(records)} correction records to {filepath}")


def output_turns_json(data: Dict[str, Any], filepath: str) -> None:
    """Write the corrected turns JSON to disk."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote corrected turns to {filepath}")


def output_summary(summary: Dict[str, Any]) -> None:
    """Print a human-readable summary to stdout."""
    print("\n========== Transcript Validation Summary ==========")
    print(f"  Total corrections applied:  {summary['total_corrections']}")
    print(f"  Turns affected:             {summary['turns_affected']}")
    print(f"  Confidence breakdown:")
    print(f"    High:   {summary['by_confidence'].get('high', 0)}")
    print(f"    Medium: {summary['by_confidence'].get('medium', 0)}")
    print(f"    Low:    {summary['by_confidence'].get('low', 0)}")
    print(f"\n  Corrections by entity type:")
    for etype, info in summary.get("by_type", {}).items():
        print(f"    [{etype}] {info['count']} corrections")
        for ex in info.get("examples", []):
            print(f"      \"{ex['variant']}\" -> \"{ex['canonical']}\"")
    print("====================================================\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage 1.5: Validate transcript turns with glossary-based corrections",
    )
    parser.add_argument(
        "turns_file",
        help="Path to turns.json (input)",
    )
    parser.add_argument(
        "--glossary",
        required=True,
        help="Path to the glossary markdown file (references/transcript-glossary.md)",
    )
    parser.add_argument(
        "--output",
        default="turns-corrected.json",
        help="Path for the corrected turns output (default: turns-corrected.json)",
    )
    parser.add_argument(
        "--corrections-output",
        default="corrections.json",
        help="Path for the corrections audit log (default: corrections.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only produce corrections.json; do not write corrected turns",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary; do not write any output files",
    )
    parser.add_argument(
        "--no-fuzzy",
        action="store_true",
        help="Skip slow fuzzy matching phase (use for large transcripts)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Load inputs
    correction_map, type_map = parse_glossary(args.glossary)
    if not correction_map:
        print(
            "Warning: empty glossary — no corrections will be applied.",
            file=sys.stderr,
        )

    data = load_turns(args.turns_file)
    print(
        f"Loaded {data['metadata'].get('total_turns', len(data.get('turns', [])))} turns "
        f"from {args.turns_file}"
    )
    print(f"Loaded {len(correction_map)} glossary entries from {args.glossary}")

    # Process
    corrections, corrected_data = process_turns(
        data, correction_map, type_map, dry_run=args.dry_run,
        skip_fuzzy=args.no_fuzzy,
    )

    # Build and display summary
    summary = build_summary(corrections, type_map)
    output_summary(summary)

    if args.summary_only:
        return

    # Write outputs
    output_corrections_json(corrections, args.corrections_output)

    if not args.dry_run and corrected_data:
        output_turns_json(corrected_data, args.output)


if __name__ == "__main__":
    main()
