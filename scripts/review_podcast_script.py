#!/usr/bin/env python3
"""Hard-rule review for model-written podcast scripts before TTS."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CHARS_PER_MINUTE = 320
MIN_TARGET_MINUTES = 3
MAX_TARGET_MINUTES = 15
CHAR_TOLERANCE = 0.18

FORBIDDEN_PATTERNS = [
    r"HOST:",
    r"GUEST:",
    r"Host:",
    r"Guest:",
    r"Estimated duration",
    r"Source duration",
    r"Target character",
    r"Duration policy",
    r"欢迎收听",
    r"本期播客将总结",
    r"这期播客将总结",
    r"\d{2}:\d{2}",
    r"从用户角度看",
    r"换成听众最关心的问题",
    r"还有一个可以带走的判断",
    r"这个判断的重点不是概念本身",
    r"资料索引",
    r"下面进入第\d+个重点",
    r"第\d+个重点，是",
]


def plain(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def source_seconds(knowledge: dict[str, Any]) -> float:
    meta = knowledge.get("metadata", {})
    duration = meta.get("duration")
    if isinstance(duration, dict) and isinstance(duration.get("total_seconds"), (int, float)):
        return float(duration["total_seconds"])
    total = meta.get("total_duration_seconds")
    if isinstance(total, (int, float)) and total > 0:
        return float(total)
    return 3600.0


def target_minutes(seconds: float) -> int:
    return max(MIN_TARGET_MINUTES, min(MAX_TARGET_MINUTES, round((seconds / 60) * 0.10)))


def nonempty_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def repeated_prefixes(paragraphs: list[str], length: int = 10) -> list[tuple[str, int]]:
    prefixes = [p[:length] for p in paragraphs if len(p) >= length]
    counts = Counter(prefixes)
    return [(prefix, count) for prefix, count in counts.items() if count >= 3]


def review(text: str, knowledge: dict[str, Any], min_chars: int | None, max_chars: int | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    compact_len = clean_count(text)

    if min_chars is None or max_chars is None:
        target = target_minutes(source_seconds(knowledge))
        target_chars = target * CHARS_PER_MINUTE
        min_chars = round(target_chars * (1 - CHAR_TOLERANCE))
        max_chars = round(target_chars * (1 + CHAR_TOLERANCE))

    if not (min_chars <= compact_len <= max_chars):
        errors.append(f"Length {compact_len} outside expected range {min_chars}-{max_chars}.")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            errors.append(f"Forbidden spoken pattern found: {pattern}")

    if re.search(r"\*\*|`", text) or re.search(r"^#{1,6}\s+", text, re.M):
        errors.append("Markdown/code/heading syntax found in script body.")

    paragraphs = nonempty_paragraphs(text)
    if len(paragraphs) < 8:
        warnings.append("Script has very few paragraphs; check whether it develops ideas enough.")

    duplicated = [p for p, count in Counter(paragraphs).items() if count > 1]
    if duplicated:
        errors.append(f"Repeated paragraph(s) found: {len(duplicated)}")

    prefix_repeats = repeated_prefixes(paragraphs)
    if prefix_repeats:
        errors.append("Mechanical repeated paragraph openings: " + ", ".join(f"{p}×{c}" for p, c in prefix_repeats[:5]))

    first_400 = text[:400]
    first_250 = text[:250]
    if not ("今天我们用" in first_250 and "核心判断" in first_250 and "主线" in first_400):
        errors.append(
            "Opening must use the standardized listener hook: start with "
            "'今天我们用[目标时长]拆解...' and state the interview's core judgment/main line."
        )

    if not re.search(r"为什么|判断|核心|问题|意味着|听懂|访谈", first_400):
        warnings.append("Opening may not establish the episode question or core judgment.")

    guest = knowledge.get("metadata", {}).get("guest", {})
    guest_name = plain(guest.get("name") if isinstance(guest, dict) else guest)
    if guest_name and guest_name not in text[:600]:
        warnings.append(f"Guest name '{guest_name}' does not appear early in the opening.")

    return errors, warnings


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review a model-written podcast script before TTS.")
    parser.add_argument("script", metavar="SCRIPT_MD", help="Podcast script path.")
    parser.add_argument("--knowledge", metavar="KNOWLEDGE_JSON", default=None, help="Optional knowledge.json for duration and guest checks.")
    parser.add_argument("--min-chars", type=int, default=None, help="Override minimum non-space character count.")
    parser.add_argument("--max-chars", type=int, default=None, help="Override maximum non-space character count.")
    return parser


def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()
    script_path = Path(args.script)
    if not script_path.is_file():
        parser.error(f"script not found: {script_path}")

    text = script_path.read_text(encoding="utf-8")
    knowledge = load_json(args.knowledge)
    errors, warnings = review(text, knowledge, args.min_chars, args.max_chars)

    print(f"Podcast review: {script_path}")
    print(f"Characters (non-space): {clean_count(text)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
    print("PASS: hard-rule podcast review passed.")


if __name__ == "__main__":
    main()
