#!/usr/bin/env python3
"""为访谈金句生成意境配图（通过 MiniMax Token Plan image-01 模型）。

从 knowledge.json 提取 Top N 条金句，为每条生成一张 4:5 比例的艺术插图，
适合在社交媒体（朋友圈/微博/小红书）传播。

用法：
    python generate_quotecards.py knowledge.json
    python generate_quotecards.py knowledge.json --count 3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from _mmx_utils import run_mmx


def pick_top_quotes(data: dict, count: int = 4) -> list[dict]:
    """从 knowledge.json 中选取 Top N 金句。"""
    quotes: list[dict] = []
    segments = data.get("segments", [])
    for seg in segments:
        for q in seg.get("golden_quotes", []):
            text = q.get("text", "").strip()
            if len(text) > 20:  # 过滤太短的金句
                quotes.append({"text": text, "timestamp": q.get("timestamp", "")})
    # 返回前 N 条
    return quotes[:count]


def build_prompt(quote_text: str) -> str:
    """为金句构造意境图 prompt。"""
    # 截取前 100 字作为 prompt 素材
    snippet = quote_text[:120]
    return (
        f"An artistic atmospheric illustration inspired by this idea: '{snippet}'. "
        f"Soft lighting, editorial minimal style, poetic mood, warm tones. "
        f"Vertical 4:5 composition with ample space for text overlay. "
        f"No letters, no words, no text in the image. "
        f"Clean sophisticated aesthetic suitable for social media sharing."
    )


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为访谈金句生成意境配图。")
    parser.add_argument("knowledge_json", metavar="KNOWLEDGE_JSON", help="knowledge.json 文件路径。")
    parser.add_argument("--output-dir", "-o", metavar="DIR", default=None, help="输出目录。")
    parser.add_argument("--count", "-n", type=int, default=4, help="生成图片数量（默认：4）。")
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_argparser()
    args = parser.parse_args(argv)

    kp = Path(args.knowledge_json)
    if not kp.is_file():
        print(f"错误：未找到文件：{kp}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(kp.read_text(encoding="utf-8"))

    quotes = pick_top_quotes(data, args.count)
    if not quotes:
        print("错误：未找到合适的金句。", file=sys.stderr)
        sys.exit(1)

    # 输出目录
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        interview_dir = kp.parent.parent
        out_dir = interview_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    interview_name = kp.parent.parent.name
    print(f"共 {len(quotes)} 条金句，开始逐条生成配图...")

    for i, q in enumerate(quotes, 1):
        prompt = build_prompt(q["text"])
        out_path = str(out_dir / f"quote-{i:02d}-{interview_name}.png")
        snippet = q["text"][:60]

        print(f"  [{i}/{len(quotes)}] {snippet}...", end=" ", flush=True)

        result = run_mmx([
            "image", "generate",
            "--prompt", prompt,
            "--aspect-ratio", "3:4",
            "--out", out_path,
            "--prompt-optimizer",
            "--quiet",
        ], timeout=120)

        if result.returncode != 0:
            print(f"失败：{result.stderr.strip()[:100]}")
            continue

        size_kb = Path(out_path).stat().st_size / 1024 if Path(out_path).is_file() else 0
        print(f"完成（{size_kb:.0f} KB）")

        # 冷却 3 秒，避免触发 TPM 限制
        if i < len(quotes):
            time.sleep(3)

    print(f"全部完成。输出目录：{out_dir}")


if __name__ == "__main__":
    main()
