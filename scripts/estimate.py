#!/usr/bin/env python3
"""Pre-run estimation report for the deepread pipeline.

Analyzes a transcript .docx file and produces a structured cost/runtime
estimation with interactive output selection.

Usage:
    python scripts/estimate.py transcript.docx
    python scripts/estimate.py transcript.docx --non-interactive
    python scripts/estimate.py transcript.docx --non-interactive --select 1,2,3,7
    python scripts/estimate.py transcript.docx --json  # pipeline-friendly mode
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional

from docx import Document


# ---------------------------------------------------------------------------
# Output definitions (fixed per-output costs from SKILL.md pipeline)
# ---------------------------------------------------------------------------

OUTPUTS = [
    {
        "id": 1,
        "name": "TL;DR 速览",
        "tokens": 5000,
        "token_display": "~5K",
        "time_min": 2,
        "time_max": 3,
        "time_display": "2-3 min",
        "dependency": "knowledge.json",
    },
    {
        "id": 2,
        "name": "深度报告",
        "tokens": 20000,
        "token_display": "~20K",
        "time_min": 5,
        "time_max": 8,
        "time_display": "5-8 min",
        "dependency": "knowledge.json",
    },
    {
        "id": 3,
        "name": "学习卡片 HTML",
        "tokens": 8000,
        "token_display": "~8K",
        "time_min": 3,
        "time_max": 5,
        "time_display": "3-5 min",
        "dependency": "visual_content.json",
    },
    {
        "id": 4,
        "name": "知识图谱 HTML",
        "tokens": 8000,
        "token_display": "~8K",
        "time_min": 3,
        "time_max": 5,
        "time_display": "3-5 min",
        "dependency": "visual_content.json",
    },
    {
        "id": 5,
        "name": "社交媒体推文",
        "tokens": 8000,
        "token_display": "~8K",
        "time_min": 2,
        "time_max": 3,
        "time_display": "2-3 min",
        "dependency": "knowledge.json",
    },
    {
        "id": 6,
        "name": "播客脚本+BGM音频",
        "tokens": 10000,
        "token_display": "~10K",
        "time_min": 7,
        "time_max": 14,
        "time_display": "7-14 min",
        "dependency": "knowledge.json + mmx CLI",
    },
    {
        "id": 7,
        "name": "PDF 报告 (x2)",
        "tokens": 0,
        "token_display": "~0K",
        "time_min": 1,
        "time_max": 2,
        "time_display": "1-2 min",
        "dependency": "Markdown 文件",
    },
]


# ---------------------------------------------------------------------------
# .docx parsing
# ---------------------------------------------------------------------------


def parse_transcript(filepath: str) -> dict:
    """Parse a .docx transcript and return turn/character/duration stats.

    Reads all paragraphs, counts turns by detecting speaker-label lines
    (paragraphs containing timestamps like '00:08' or '01:23:45'), and
    estimates total interview duration from the last timestamp found.
    Falls back to a character-count heuristic (~250 Chinese chars/min)
    when no usable timestamps are present.
    """
    doc = Document(filepath)

    total_chars = 0
    turns = 0
    timestamps_seconds: list[int] = []
    timestamp_pattern = re.compile(r"(\d{1,2}:)?\d{1,2}:\d{2}")

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        total_chars += len(text)

        if timestamp_pattern.search(text):
            turns += 1
            match = timestamp_pattern.search(text)
            assert match is not None
            ts_str = match.group(0)
            seconds = _parse_timestamp(ts_str)
            if seconds is not None and seconds > 0:
                timestamps_seconds.append(seconds)

    # Duration estimation: prefer last timestamp, fall back to char count
    if timestamps_seconds and max(timestamps_seconds) > 60:
        estimated_duration_seconds = max(timestamps_seconds)
    else:
        # Chinese conversational speech: ~250 characters per minute
        estimated_duration_seconds = int((total_chars / 250) * 60)

    duration_minutes = round(estimated_duration_seconds / 60, 1)

    return {
        "turns": turns,
        "total_chars": total_chars,
        "estimated_duration_seconds": estimated_duration_seconds,
        "estimated_duration_minutes": duration_minutes,
    }


def _parse_timestamp(ts: str) -> Optional[int]:
    """Parse 'HH:MM:SS' or 'MM:SS' into total seconds."""
    parts = ts.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return None


# ---------------------------------------------------------------------------
# Estimation logic
# ---------------------------------------------------------------------------

# Pipeline baseline: ~2,000 tokens consumed per minute of interview for the
# full pipeline (Parse -> Validate -> Segment -> Extract -> Synthesize).
TOKENS_PER_MINUTE = 2000


def estimate_pipeline(stats: dict) -> dict:
    """Produce per-output and pipeline-level token/runtime estimates.

    Pipeline token cost scales with interview length (~2K tokens/min).
    Per-output costs are fixed estimates from the SKILL.md pipeline table.
    Total runtime is the sum of per-output times (sequential execution).
    """
    minutes = stats["estimated_duration_minutes"]
    pipeline_tokens = int(minutes * TOKENS_PER_MINUTE)

    output_total_tokens = sum(o["tokens"] for o in OUTPUTS)
    total_tokens = pipeline_tokens + output_total_tokens

    # Sequential runtime: pipeline (1.0x-1.5x interview length) + sum of per-output times
    pipeline_runtime_min = max(int(minutes * 1.0), 10)
    pipeline_runtime_max = max(int(minutes * 1.5), 20)
    output_runtime_min = sum(o["time_min"] for o in OUTPUTS)
    output_runtime_max = sum(o["time_max"] for o in OUTPUTS)

    runtime_min = pipeline_runtime_min + output_runtime_min
    runtime_max = pipeline_runtime_max + output_runtime_max

    return {
        "pipeline_tokens": pipeline_tokens,
        "output_tokens": output_total_tokens,
        "total_tokens": total_tokens,
        "pipeline_runtime_min": pipeline_runtime_min,
        "pipeline_runtime_max": pipeline_runtime_max,
        "output_runtime_min": output_runtime_min,
        "output_runtime_max": output_runtime_max,
        "runtime_min": runtime_min,
        "runtime_max": runtime_max,
    }


def format_tokens(n: int) -> str:
    """Format a token count as a human-readable string."""
    if n >= 1000:
        return f"~{n // 1000}K"
    return str(n)


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def print_report(stats: dict, estimation: dict) -> None:
    """Print the full estimation report to stdout."""

    def _hms(seconds: int) -> str:
        """Seconds -> HH:MM:SS string."""
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    dur_sec = stats["estimated_duration_seconds"]
    dur_label = _hms(dur_sec)

    print()
    print("=" * 72)
    print("  Interview-Based Learning -- 运行前估算报告")
    print("=" * 72)
    print()
    print(f"  访谈轮次:        {stats['turns']} 轮")
    print(f"  总字符数:        {stats['total_chars']:,}")
    print(f"  预估时长:        {stats['estimated_duration_minutes']} 分钟  ({dur_label})")
    print()
    print(f"  流水线 Token 估算:   {format_tokens(estimation['pipeline_tokens']):>6}   (基准: ~2K / 分钟)")
    print(f"  流水线耗时估算:      {estimation['pipeline_runtime_min']}-{estimation['pipeline_runtime_max']} 分钟")
    print()
    print(f"  所有输出 Token 合计: {format_tokens(estimation['output_tokens']):>6}")
    print(f"  所有输出耗时合计:    {estimation['output_runtime_min']}-{estimation['output_runtime_max']} 分钟")
    print()
    print(f"  总计 Token 估算:     {format_tokens(estimation['total_tokens']):>6}")
    print(f"  总计耗时估算:        {estimation['runtime_min']}-{estimation['runtime_max']} 分钟")
    print()

    # --- Per-output breakdown table ---
    header = (
        f"  {'#':<4}"
        f"{'输出':<18}"
        f"{'Token 消耗':<12}"
        f"{'预计耗时':<12}"
        f"{'依赖':<24}"
    )
    sep = "-" * 72
    print(sep)
    print(header)
    print(sep)

    for o in OUTPUTS:
        print(
            f"  {o['id']:<4}"
            f"{o['name']:<18}"
            f"{o['token_display']:<12}"
            f"{o['time_display']:<12}"
            f"{o['dependency']:<24}"
        )

    print(sep)
    print()


def print_selection_summary(selected: list[int]) -> None:
    """Print a summary of selected outputs with aggregate estimates."""
    sel_set = set(selected)
    sel_objs = [o for o in OUTPUTS if o["id"] in sel_set]

    tokens = sum(o["tokens"] for o in sel_objs)
    t_min = sum(o["time_min"] for o in sel_objs)
    t_max = sum(o["time_max"] for o in sel_objs)

    names = [o["name"] for o in sel_objs]
    print()
    print(f"  已选择 {len(selected)} 个输出: {', '.join(names)}")
    print(f"  所选输出 Token 合计:  {format_tokens(tokens)}")
    print(f"  所选输出预计耗时:     {t_min}-{t_max} 分钟")


# ---------------------------------------------------------------------------
# Interactive selection
# ---------------------------------------------------------------------------


def interactive_select(
    non_interactive: bool = False,
    preselected: Optional[str] = None,
) -> list[int]:
    """Prompt the user to select which outputs to generate.

    In non-interactive mode, returns the preselected set (or all outputs if none).
    In interactive mode, displays a numbered checklist and accepts input
    like '1,2,3,7', '1-4,7', or 'all'.
    """
    if non_interactive:
        selected = _parse_selection(preselected) if preselected else [o["id"] for o in OUTPUTS]
        print(f"\n  [非交互模式] 已选择输出: {selected}")
        return selected

    print("  请选择要生成的输出 (输入编号, 逗号或短横分隔, 或输入 'all'):")
    print()
    for o in OUTPUTS:
        print(f"    [{o['id']}] {o['name']}")
    print()

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  已取消。")
            sys.exit(0)

        if not raw:
            print("  输入不能为空, 请重试。")
            continue

        if raw.lower() == "all":
            return [o["id"] for o in OUTPUTS]

        selected = _parse_selection(raw)
        if selected:
            return selected

        print("  无法解析输入。请输入类似 '1,2,3,7'、'1-4' 或 'all'。")


def _parse_selection(raw: str) -> list[int]:
    """Parse selection string into a sorted, deduplicated list of ints.

    Supports comma-separated values and ranges: '1,2,3,7' or '1-4,7'.
    Returns an empty list when parsing fails entirely.
    """
    try:
        ids: list[int] = []
        for part in raw.split(","):
            part = part.strip()
            if "-" in part:
                lo, hi = part.split("-", 1)
                ids.extend(range(int(lo.strip()), int(hi.strip()) + 1))
            else:
                ids.append(int(part))
        valid_ids = {o["id"] for o in OUTPUTS}
        valid = sorted(set(i for i in ids if i in valid_ids))
        return valid
    except (ValueError, IndexError):
        return []


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="访谈笔录流水线运行前估算 — 分析 .docx 并输出 Token / 耗时估算",
    )
    parser.add_argument(
        "transcript",
        help="访谈笔录 .docx 文件路径",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="跳过交互式选择, 默认选中全部 7 个用户输出",
    )
    parser.add_argument(
        "--select",
        type=str,
        default=None,
        help="在非交互模式下指定输出编号, 如 '1,2,3,7'、'1-4' 或 'all'",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="仅输出最终选择结果为 JSON (供其他脚本管道调用)",
    )

    args = parser.parse_args()

    # -- Parse transcript ----------------------------------------------------
    try:
        stats = parse_transcript(args.transcript)
    except Exception as exc:
        print(f"错误: 无法解析文件 '{args.transcript}': {exc}", file=sys.stderr)
        sys.exit(1)

    estimation = estimate_pipeline(stats)

    # -- JSON-only pipeline mode ---------------------------------------------
    if args.json:
        selected = interactive_select(
            non_interactive=True,
            preselected=args.select,
        )
        result = {
            "transcript": args.transcript,
            "stats": stats,
            "estimation": estimation,
            "selected": selected,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # -- Full report + interactive selection ---------------------------------
    print_report(stats, estimation)

    selected = interactive_select(
        non_interactive=args.non_interactive,
        preselected=args.select,
    )

    print_selection_summary(selected)

    # Final JSON line for downstream scripts
    print()
    print(json.dumps({"selected": selected}, ensure_ascii=False))


if __name__ == "__main__":
    main()
