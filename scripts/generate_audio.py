#!/usr/bin/env python3
"""将播客脚本 Markdown 文件通过 MiniMax Token Plan (mmx CLI) 转换为 MP3 音频。

使用 MiniMax speech-2.8 系列模型进行中文语音合成。
支持多种语音、语速、音调控制。单次最多 10,000 字符。

用法：
    python generate_audio.py podcast-script.md
    python generate_audio.py podcast-script.md --output podcast.mp3
    python generate_audio.py podcast-script.md --model speech-2.8-hd
    python generate_audio.py podcast-script.md --voice presenter_male --speed 1.2

前置条件：
    npm install -g mmx-cli
    mmx auth login --api-key sk-cp-...
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "speech-2.8-hd"
DEFAULT_VOICE = "presenter_male"
DEFAULT_SPEED = 1.2
CHARS_PER_SECOND = 4.0

VOICE_OPTIONS = [
    "male-qn-qingse",       "male-qn-jingying",
    "male-qn-badao",         "male-qn-daxuesheng",
    "female-shaonv",         "female-yujie",
    "female-chengshu",       "female-tianmei",
    "presenter_male",        "presenter_female",
    "audiobook_male_1",      "audiobook_female_1",
    "clever_boy",            "cute_boy",
    "lovely_girl",           "junlang_nanyou",
    "wumei_yujie",           "tianxin_xiaoling",
]


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_markdown(raw: str) -> str:
    """从 Markdown 播客脚本中提取纯文本。"""
    text = raw
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\(.*?\)", r"\1", text)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^={3,}.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"【[^】]*】", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def estimate_duration(text: str) -> str:
    """估算纯文本的朗读时长。"""
    chars = len(text.replace("\n", "").replace(" ", ""))
    seconds = chars / CHARS_PER_SECOND
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}分{secs}秒（{chars} 字符，按 {CHARS_PER_SECOND} 字/秒估算）"


# ---------------------------------------------------------------------------
# mmx CLI helper
# ---------------------------------------------------------------------------

def _find_mmx() -> Optional[str]:
    """查找 mmx CLI 可执行文件。"""
    # 先尝试 PATH
    found = shutil.which("mmx")
    if found:
        return found
    # 常见 npm global 路径
    candidates = [
        Path.home() / "AppData" / "Roaming" / "npm" / "mmx.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "mmx",
        Path("/usr/local/bin/mmx"),
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="将播客脚本 Markdown 文件通过 MiniMax Token Plan 转换为 MP3 音频。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""示例：
  python generate_audio.py podcast-script.md
  python generate_audio.py podcast-script.md --model speech-2.8-hd
  python generate_audio.py podcast-script.md --voice presenter_male --speed 1.2

前置条件：
  npm install -g mmx-cli
  mmx auth login --api-key sk-cp-...

文档：https://platform.minimaxi.com/docs/token-plan/minimax-cli
""",
    )
    parser.add_argument("input", metavar="INPUT_MD", help="输入的播客脚本 Markdown 文件路径。")
    parser.add_argument("--output", "-o", metavar="PATH", default=None, help="输出 MP3 文件路径。")
    parser.add_argument("--model", "-m", metavar="MODEL", default=DEFAULT_MODEL, help=f"模型 ID（默认：{DEFAULT_MODEL}）。")
    parser.add_argument("--voice", "-v", metavar="VOICE_ID", default=DEFAULT_VOICE, help=f"语音 ID（默认：{DEFAULT_VOICE}）。")
    parser.add_argument("--speed", metavar="FLOAT", type=float, default=DEFAULT_SPEED, help=f"语速倍率（默认：{DEFAULT_SPEED}）。")
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_argparser()
    args = parser.parse_args(argv)

    # --- 验证 mmx CLI ---
    mmx_bin = _find_mmx()
    if not mmx_bin:
        print("错误：未找到 mmx 命令。", file=sys.stderr)
        print("请先安装：npm install -g mmx-cli", file=sys.stderr)
        print("然后认证：mmx auth login --api-key sk-cp-...", file=sys.stderr)
        sys.exit(1)

    # --- 验证输入 ---
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"错误：未找到输入文件：{input_path}", file=sys.stderr)
        sys.exit(1)

    # --- 输出路径 ---
    output_path = args.output or str(input_path.with_suffix(".mp3"))

    # --- 解析 Markdown ---
    raw_text = input_path.read_text(encoding="utf-8")
    plain_text = parse_markdown(raw_text)
    if not plain_text.strip():
        print("错误：解析 Markdown 后未找到可合成文本。", file=sys.stderr)
        sys.exit(1)

    # --- 打印信息 ---
    print(f"输入文件：  {input_path}")
    print(f"模型：      {args.model}")
    print(f"语音：      {args.voice}")
    print(f"语速：      {args.speed}x")
    print(f"输出文件：  {output_path}")
    print(f"预计时长：  {estimate_duration(plain_text)}")
    print()

    # --- 写入临时文件，通过 --text-file 传入 ---
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False
    )
    try:
        tmp.write(plain_text)
        tmp.close()

        cmd = [
            mmx_bin, "speech", "synthesize",
            "--model", args.model,
            "--voice", args.voice,
            "--speed", str(args.speed),
            "--text-file", tmp.name,
            "--out", output_path,
        ]

        print("正在合成语音...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"合成失败：{result.stderr}", file=sys.stderr)
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("合成超时（300 秒）", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            Path(tmp.name).unlink()
        except OSError:
            pass

    # --- 确认输出 ---
    out_file = Path(output_path)
    if out_file.is_file() and out_file.stat().st_size > 0:
        size_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"完成：{output_path}（{size_mb:.1f} MB）")
    else:
        print(f"错误：输出文件未生成：{output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
