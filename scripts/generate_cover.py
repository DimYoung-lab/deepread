#!/usr/bin/env python3
"""为访谈生成封面图（通过 MiniMax Token Plan image-01 模型）。

从 knowledge.json 提取核心主题和嘉宾信息，构造 prompt 生成
一张 2:3 比例的杂志风格封面图。

用法：
    python generate_cover.py knowledge.json
    python generate_cover.py knowledge.json --output images/cover.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from _mmx_utils import run_mmx


def extract_theme(data: dict) -> str:
    """从 knowledge.json 提取封面 prompt 所需信息。"""
    meta = data.get("metadata", {})
    guest = meta.get("guest", {}).get("name", "") if isinstance(meta.get("guest"), dict) else ""
    themes = data.get("cross_cutting_themes", [])
    theme_names = [t.get("theme", "") for t in themes[:5] if t.get("theme")]

    # 构造主题描述
    topic_str = "、".join(theme_names[:3]) if theme_names else "深度访谈"
    guest_str = f" featuring {guest}" if guest else ""
    return guest_str, topic_str


def build_prompt(guest_str: str, topic_str: str) -> str:
    """构造图片生成 prompt。"""
    return (
        f"A minimalist editorial magazine cover illustration. "
        f"Theme: {topic_str}{guest_str}. "
        f"Clean composition with generous negative space for typography overlay. "
        f"Warm cream and burgundy color palette. "
        f"Abstract geometric elements, sophisticated literary aesthetic. "
        f"No text or letters in the image. "
        f"Professional magazine cover quality."
    )


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成访谈封面图。")
    parser.add_argument("knowledge_json", metavar="KNOWLEDGE_JSON", help="knowledge.json 文件路径。")
    parser.add_argument("--output", "-o", metavar="PATH", default=None, help="输出图片路径。")
    parser.add_argument("--aspect-ratio", default="2:3", help="宽高比（默认：2:3）。")
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_argparser()
    args = parser.parse_args(argv)

    # 读取 knowledge.json
    kp = Path(args.knowledge_json)
    if not kp.is_file():
        print(f"错误：未找到文件：{kp}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(kp.read_text(encoding="utf-8"))

    # 提取主题
    guest_str, topic_str = extract_theme(data)
    prompt = build_prompt(guest_str, topic_str)

    # 确定输出路径
    if args.output:
        out = args.output
    else:
        parent = kp.parent.parent  # data/ → interview dir
        img_dir = parent / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        # 从目录名提取 guest-date
        interview_name = parent.name
        out = str(img_dir / f"cover-{interview_name}.png")

    print(f"主题：{topic_str}")
    print(f"输出：{out}")
    print(f"正在生成封面图...")

    result = run_mmx([
        "image", "generate",
        "--prompt", prompt,
        "--aspect-ratio", args.aspect_ratio,
        "--out", out,
        "--prompt-optimizer",
        "--quiet",
    ], timeout=120)

    if result.returncode != 0:
        print(f"生成失败：{result.stderr}", file=sys.stderr)
        sys.exit(1)

    if Path(out).is_file():
        size_kb = Path(out).stat().st_size / 1024
        print(f"完成：{out}（{size_kb:.0f} KB）")
    else:
        print(f"错误：输出文件未生成", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
