#!/usr/bin/env python3
"""为播客音频叠加背景音乐（通过 MiniMax Token Plan music-2.6 模型）。

生成与访谈主题匹配的 instrumental 背景音乐，然后用 pydub 将其
与播客人声混合（BGM 音量降至 18%，loop 至与人声等长）。

用法：
    python generate_bgm_podcast.py podcast.mp3
    python generate_bgm_podcast.py podcast.mp3 --knowledge knowledge.json
    python generate_bgm_podcast.py podcast.mp3 --output podcast-bgm.mp3
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Optional

from _mmx_utils import run_mmx


def build_music_prompt(data: dict | None) -> str:
    """根据访谈主题构造背景音乐 prompt。"""
    if data:
        themes = data.get("cross_cutting_themes", [])
        theme_names = [t.get("theme", "") for t in themes[:3]]
        mood = "、".join(theme_names) if theme_names else "科技与人文"
    else:
        mood = "深度对话与思考"

    return (
        f"Warm, contemplative instrumental background music for a podcast about {mood}. "
        f"Soft piano and subtle synthesizer pads, very light percussion, "
        f"moderate slow tempo around 80 BPM, unobtrusive and calming. "
        f"No dramatic changes, no loud sections, consistent volume throughout. "
        f"Suitable for speech overlay."
    )


def mix_audio(voice_path: str, bgm_path: str, output_path: str) -> None:
    """将 BGM 与人声混合。BGM 音量降至 18%，loop 至与人声等长。"""
    from pydub import AudioSegment

    voice = AudioSegment.from_file(voice_path)
    bgm = AudioSegment.from_file(bgm_path)

    # BGM 音量降至 18%
    bgm = bgm - 15  # -15 dB ≈ 18% volume

    # Loop BGM 至覆盖人声长度
    voice_duration = len(voice)
    if len(bgm) < voice_duration:
        loops = (voice_duration // len(bgm)) + 1
        bgm = bgm * loops
    bgm = bgm[:voice_duration]

    # 叠加（overlay）
    mixed = voice.overlay(bgm)
    mixed.export(output_path, format="mp3", bitrate="192k")


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为播客音频叠加背景音乐。")
    parser.add_argument("podcast_mp3", metavar="PODCAST_MP3", help="播客 MP3 文件路径。")
    parser.add_argument("--knowledge", "-k", metavar="JSON", default=None, help="knowledge.json 路径（用于提取主题）。")
    parser.add_argument("--output", "-o", metavar="PATH", default=None, help="输出路径。")
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_argparser()
    args = parser.parse_args(argv)

    voice_path = Path(args.podcast_mp3)
    if not voice_path.is_file():
        print(f"错误：未找到播客文件：{voice_path}", file=sys.stderr)
        sys.exit(1)

    # 读取知识库（可选）
    data = None
    if args.knowledge:
        kp = Path(args.knowledge)
        if kp.is_file():
            data = json.loads(kp.read_text(encoding="utf-8"))

    prompt = build_music_prompt(data)

    # 输出路径
    if args.output:
        out = args.output
    else:
        stem = voice_path.stem
        out = str(voice_path.parent / f"{stem}-bgm.mp3")

    # Step 1: 生成 BGM（保存到音频目录）
    bgm_path = str(voice_path.parent / f"bgm-{voice_path.stem}.mp3")
    print(f"正在生成背景音乐...")

    result = run_mmx([
        "music", "generate",
        "--prompt", prompt,
        "--instrumental",
        "--out", bgm_path,
        "--quiet",
    ], timeout=180)

    if result.returncode != 0:
        print(f"音乐生成失败：{result.stderr}", file=sys.stderr)
        sys.exit(1)

    bgm_size = Path(bgm_path).stat().st_size / 1024 if Path(bgm_path).is_file() else 0
    print(f"背景音乐已生成（{bgm_size:.0f} KB）：{bgm_path}")

    # Step 2: 混音
    print(f"正在混合音频...")
    try:
        mix_audio(str(voice_path), bgm_path, out)
    except Exception as exc:
        print(f"混音失败：{exc}", file=sys.stderr)
        print("提示：需要安装 pydub：pip install pydub", file=sys.stderr)
        print(f"原始 BGM 文件已保存：{bgm_path}")
        sys.exit(1)

    if Path(out).is_file():
        size_mb = Path(out).stat().st_size / (1024 * 1024)
        print(f"完成：{out}（{size_mb:.1f} MB）")
    else:
        print(f"错误：输出文件未生成", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
