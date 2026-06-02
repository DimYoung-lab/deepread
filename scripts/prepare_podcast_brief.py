#!/usr/bin/env python3
"""Prepare an editorial brief for a model-written podcast script.

This script intentionally does not generate the final podcast transcript.
It extracts source material, duration policy, and editorial constraints so a
language model can write a natural, listener-centered script.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CHARS_PER_MINUTE = 320
MIN_TARGET_MINUTES = 3
MAX_TARGET_MINUTES = 15
CHAR_TOLERANCE = 0.12


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def plain(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\s+", " ", text).strip()


def clip(value: Any, limit: int) -> str:
    text = plain(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip("，,。；; ") + "。"


def first_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return ""


def seconds_from_metadata(metadata: dict[str, Any]) -> float | None:
    duration = metadata.get("duration")
    if isinstance(duration, dict):
        total = duration.get("total_seconds")
        if isinstance(total, (int, float)) and total > 0:
            return float(total)
    total = metadata.get("total_duration_seconds")
    if isinstance(total, (int, float)) and total > 0:
        return float(total)
    return None


def max_timestamp_seconds(turns_data: dict[str, Any]) -> float | None:
    max_ts = 0.0
    for turn in turns_data.get("turns", []):
        ts = turn.get("timestamp_seconds")
        if isinstance(ts, (int, float)):
            max_ts = max(max_ts, float(ts))
    return max_ts or None


def estimate_seconds_from_text(turns_data: dict[str, Any]) -> float | None:
    chars = sum(len(plain(turn.get("text"))) for turn in turns_data.get("turns", []))
    if chars <= 0:
        return None
    return chars / 300 * 60


def source_duration_seconds(knowledge: dict[str, Any], turns_data: dict[str, Any]) -> tuple[float, str]:
    knowledge_seconds = seconds_from_metadata(knowledge.get("metadata", {}))
    if knowledge_seconds:
        return knowledge_seconds, "knowledge.metadata"

    turns_seconds = seconds_from_metadata(turns_data.get("metadata", {}))
    if turns_seconds:
        return turns_seconds, "turns.metadata"

    timestamp_seconds = max_timestamp_seconds(turns_data)
    if timestamp_seconds:
        return timestamp_seconds, "turns.max_timestamp"

    estimated_seconds = estimate_seconds_from_text(turns_data)
    if estimated_seconds:
        return estimated_seconds, "turns.text_estimate"

    return 60 * 60, "default_60_min"


def target_minutes_from_source(source_seconds: float) -> int:
    source_minutes = source_seconds / 60
    return max(MIN_TARGET_MINUTES, min(MAX_TARGET_MINUTES, round(source_minutes * 0.10)))


def output_default_path(knowledge_path: Path, metadata: dict[str, Any]) -> Path:
    date = plain(metadata.get("date")) or "undated"
    guest = metadata.get("guest", {})
    guest_name = plain(guest.get("name") if isinstance(guest, dict) else guest) or "guest"
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", guest_name).lower() or "guest"
    if knowledge_path.parent.name == "data":
        return knowledge_path.parent.parent / "audio" / f"podcast-brief-{slug}-{date}.md"
    return knowledge_path.with_name(f"podcast-brief-{slug}-{date}.md")


def select_themes(knowledge: dict[str, Any], visual: dict[str, Any], target_minutes: int) -> list[dict[str, Any]]:
    visual_themes = visual.get("themes")
    if isinstance(visual_themes, list) and visual_themes:
        themes = [theme for theme in visual_themes if isinstance(theme, dict)]
    else:
        themes = [theme for theme in knowledge.get("cross_cutting_themes", []) if isinstance(theme, dict)]

    if not themes:
        themes = [
            {
                "name": segment.get("title"),
                "summary": segment.get("summary"),
                "highlighted_insights": segment.get("insights", [])[:2],
                "highlighted_quotes": segment.get("golden_quotes", [])[:1],
            }
            for segment in knowledge.get("segments", [])
            if isinstance(segment, dict)
        ]

    theme_count = max(4, min(7, round(target_minutes * 0.7)))
    return themes[:theme_count]


def collect_quotes(theme: dict[str, Any]) -> list[dict[str, Any]]:
    quotes: list[dict[str, Any]] = []
    for insight in theme.get("highlighted_insights", []) or []:
        if isinstance(insight, dict) and isinstance(insight.get("key_quote"), dict):
            quotes.append(insight["key_quote"])
    for quote in theme.get("highlighted_quotes", []) or []:
        if isinstance(quote, dict):
            quotes.append(quote)
    return quotes


def brief_markdown(
    knowledge: dict[str, Any],
    visual: dict[str, Any],
    turns_data: dict[str, Any],
    target_minutes: int | None,
) -> tuple[str, dict[str, Any]]:
    metadata = knowledge.get("metadata", {})
    source_seconds, duration_source = source_duration_seconds(knowledge, turns_data)
    target = target_minutes or target_minutes_from_source(source_seconds)
    target_chars = target * CHARS_PER_MINUTE
    min_chars = round(target_chars * (1 - CHAR_TOLERANCE))
    max_chars = round(target_chars * (1 + CHAR_TOLERANCE))

    title = plain(metadata.get("title")) or "这场访谈"
    guest = metadata.get("guest", {})
    guest_name = plain(guest.get("name") if isinstance(guest, dict) else guest) or "嘉宾"
    themes = select_themes(knowledge, visual, target)

    lines = [
        "# Podcast Editorial Brief",
        "",
        "## Episode",
        f"- Title: {title}",
        f"- Guest: {guest_name}",
        f"- Source duration: {round(source_seconds / 60)} minutes ({duration_source})",
        f"- Target audio: about {target} minutes",
        f"- Target script length: {min_chars}-{max_chars} non-space characters",
        "",
        "## Listener Job",
        "- Audience: people who do not have time to watch the full interview.",
        "- Promise: explain what the guest believes, why they believe it, what is at stake, and what the listener should remember.",
        "- Do not produce a report index, timeline recap, quote catalog, or evidence locator.",
        "",
        "## Script Requirements",
        "- Write the final script with the language model, not by mechanically stitching this brief.",
        "- Use natural spoken Chinese. It should sound like a polished solo podcast host.",
        "- Start with a real opening hook, then quickly state the episode's central question or conclusion.",
        "- Connect ideas with reasoning and narrative flow. Do not enumerate JSON fields.",
        "- Use quotes sparingly. When quoting, do not speak timestamps aloud.",
        "- No HOST/GUEST labels, no markdown headings, no metadata headers, no source timestamps in the spoken script.",
        "- Forbidden phrases: 从用户角度看, 换成听众最关心的问题, 还有一个可以带走的判断, 这个判断的重点不是概念本身, 资料索引, 下面进入第几个重点.",
        "",
        "## Suggested Narrative Spine",
        f"1. Why this interview matters: what {guest_name} is really trying to say.",
        "2. The core judgment: the biggest belief underneath the conversation.",
        "3. The reasoning: why this belief changes product, organization, and strategy decisions.",
        "4. The tension: what is hard, uncertain, or easy to misunderstand.",
        "5. The takeaway: what a busy listener should remember after one listen.",
        "",
        "## Source Material",
    ]

    for index, theme in enumerate(themes, start=1):
        name = plain(first_value(theme.get("name"), theme.get("theme"), theme.get("title"))) or f"Theme {index}"
        summary = clip(first_value(theme.get("summary"), theme.get("description"), theme.get("narrative")), 260)
        lines.extend(["", f"### {index}. {name}", f"- What it means: {summary}"])

        insights = theme.get("highlighted_insights")
        if not isinstance(insights, list):
            insights = theme.get("insights") if isinstance(theme.get("insights"), list) else []
        for insight in insights[:2]:
            if not isinstance(insight, dict):
                continue
            claim = clip(first_value(insight.get("claim"), insight.get("explanation"), insight.get("text")), 180)
            if claim:
                lines.append(f"- Usable interpretation: {claim}")

        for quote in collect_quotes(theme)[:1]:
            text = clip(quote.get("text"), 120)
            timestamp = plain(first_value(quote.get("timestamp"), quote.get("source_timestamp")))
            if text:
                suffix = f" (source {timestamp}; do not speak timestamp)" if timestamp else ""
                lines.append(f"- Optional quote: {text}{suffix}")

    open_questions = knowledge.get("open_questions")
    if isinstance(open_questions, list) and open_questions:
        lines.extend(["", "## Useful Tensions / Open Questions"])
        for item in open_questions[:4]:
            if isinstance(item, dict):
                question = first_value(item.get("question"), item.get("tension"), item.get("description"))
                context = first_value(item.get("context"), item.get("why_it_matters"), item.get("note"))
                if question:
                    lines.append(f"- {clip(question, 120)} {clip(context, 100)}".rstrip())
            elif item:
                lines.append(f"- {clip(item, 160)}")

    stats = {
        "source_seconds": source_seconds,
        "duration_source": duration_source,
        "target_minutes": target,
        "target_chars": target_chars,
        "min_chars": min_chars,
        "max_chars": max_chars,
    }
    return "\n".join(lines).strip() + "\n", stats


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a podcast editorial brief from knowledge.json.")
    parser.add_argument("knowledge", metavar="KNOWLEDGE_JSON", help="Path to knowledge.json.")
    parser.add_argument("--turns", metavar="TURNS_JSON", default=None, help="Optional turns-corrected.json or turns.json.")
    parser.add_argument("--visual", metavar="VISUAL_JSON", default=None, help="Optional visual_content.json.")
    parser.add_argument("--output", "-o", metavar="PATH", default=None, help="Output podcast brief path.")
    parser.add_argument("--target-minutes", type=int, default=None, help="Override adaptive duration target.")
    return parser


def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()
    if args.target_minutes is not None and not (MIN_TARGET_MINUTES <= args.target_minutes <= MAX_TARGET_MINUTES):
        parser.error(f"--target-minutes must be between {MIN_TARGET_MINUTES} and {MAX_TARGET_MINUTES}")

    knowledge_path = Path(args.knowledge)
    knowledge = load_json(args.knowledge)
    turns_data = load_json(args.turns)
    visual = load_json(args.visual)

    text, stats = brief_markdown(knowledge, visual, turns_data, args.target_minutes)
    output_path = Path(args.output) if args.output else output_default_path(knowledge_path, knowledge.get("metadata", {}))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

    print(f"Podcast brief written: {output_path}")
    print(
        "Duration policy: "
        f"source={stats['source_seconds']:.0f}s ({stats['duration_source']}), "
        f"target={stats['target_minutes']}min, "
        f"script_chars={stats['min_chars']}-{stats['max_chars']}"
    )


if __name__ == "__main__":
    main()
