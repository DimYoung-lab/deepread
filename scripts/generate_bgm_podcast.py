#!/usr/bin/env python3
"""为播客音频叠加背景音乐（通过 MiniMax Token Plan music-2.6 模型）。

生成与访谈主题匹配的 instrumental 背景音乐，然后用 ffmpeg 将其
与播客人声混合（BGM 音量 25%，loop 至与人声等长）。
默认会把混音结果写回输入播客路径，并删除纯 BGM 临时文件，让最终
audio 目录只保留一个用户可见的 podcast-*.mp3。

用法：
    python generate_bgm_podcast.py podcast.mp3
    python generate_bgm_podcast.py podcast.mp3 --knowledge knowledge.json
    python generate_bgm_podcast.py podcast.mp3 --output podcast.mp3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from _mmx_utils import run_mmx


def build_music_prompt(data: dict | None) -> str:
    """根据访谈主题构造背景音乐 prompt。"""
    if data:
        themes = data.get("cross_cutting_themes", [])
        theme_names = [t.get("theme") or t.get("name") or "" for t in themes[:3]]
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
    """将 BGM 与人声混合。BGM 音量 25%，loop 至与人声等长。

    使用 ffmpeg 直接处理（兼容 Python 3.13+ 无 audioop 模块）。"""
    import shutil

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        # Fallback: try common winget path
        winget_ffmpeg = (
            Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet"
            / "Packages" / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        )
        for root, dirs, _ in os.walk(str(winget_ffmpeg)):
            candidate = os.path.join(root, "ffmpeg.exe")
            if os.path.isfile(candidate):
                ffmpeg = candidate
                break
    if not ffmpeg:
        raise RuntimeError("未找到 ffmpeg，请安装：winget install Gyan.FFmpeg")

    # Step 1: Get voice duration (seconds)
    probe = subprocess.run(
        [ffmpeg, "-i", voice_path, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    # Parse duration from stderr
    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
    if not duration_match:
        raise RuntimeError("无法获取人声文件时长")
    h, m, s = duration_match.groups()
    voice_dur = int(h) * 3600 + int(m) * 60 + float(s)

    output = Path(output_path)
    output_tmp = output.with_name(f"{output.stem}.mix_tmp{output.suffix}")
    bgm_quiet = output.with_name(f"{output.stem}.bgm_tmp{output.suffix}")
    if str(output_tmp) == voice_path:
        output_tmp = output.with_name(f"{output.stem}.mix_tmp_2{output.suffix}")

    # Step 2: Lower BGM volume to 25% (about -12dB)
    subprocess.run([
        ffmpeg, "-y", "-i", bgm_path,
        "-filter:a", "volume=0.25",
        "-b:a", "192k", str(bgm_quiet),
    ], capture_output=True, check=True)

    # Step 3: Mix — loop BGM to match voice duration, then merge
    # ffmpeg amix: loops BGM with aloop, then mixes with voice
    loop_count = max(1, int(voice_dur / 30) + 2)  # estimate loops from ~30s BGM
    subprocess.run([
        ffmpeg, "-y",
        "-i", voice_path,
        "-stream_loop", str(loop_count), "-i", str(bgm_quiet),
        "-filter_complex", f"[1:a]atrim=0:{voice_dur}[bgm];[0:a][bgm]amix=inputs=2:duration=first:weights=1 0.25",
        "-b:a", "192k", str(output_tmp),
    ], capture_output=True, check=True)

    output_tmp.replace(output)

    for temp in (bgm_quiet,):
        try:
            temp.unlink()
        except OSError:
            pass


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为播客音频叠加背景音乐。")
    parser.add_argument("podcast_mp3", metavar="PODCAST_MP3", help="播客 MP3 文件路径。")
    parser.add_argument("--knowledge", "-k", metavar="JSON", default=None, help="knowledge.json 路径（用于提取主题）。")
    parser.add_argument("--output", "-o", metavar="PATH", default=None, help="输出路径。默认覆盖输入播客文件。")
    parser.add_argument("--keep-bgm", action="store_true", help="保留纯 BGM 文件（默认删除，避免最终目录出现多个 MP3）。")
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
    out = str(Path(args.output)) if args.output else str(voice_path)

    # Step 1: 生成临时 BGM。默认完成混音后删除，避免用户看到多个音频文件。
    bgm_path = str(voice_path.parent / f"{voice_path.stem}.bgm_source_tmp.mp3")
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
        print("提示：需要安装 ffmpeg：winget install Gyan.FFmpeg", file=sys.stderr)
        print(f"原始 BGM 文件已保存：{bgm_path}")
        sys.exit(1)

    if Path(out).is_file():
        if not args.keep_bgm:
            try:
                Path(bgm_path).unlink()
            except OSError:
                pass
        size_mb = Path(out).stat().st_size / (1024 * 1024)
        print(f"完成：{out}（{size_mb:.1f} MB）")
        if not args.keep_bgm:
            print("已清理纯 BGM 临时文件；最终只保留一个播客 MP3。")
    else:
        print(f"错误：输出文件未生成", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
