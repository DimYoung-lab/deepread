#!/usr/bin/env python3
"""Convert a podcast script markdown file to MP3 audio using edge-tts.

Usage:
    python generate_audio.py podcast-script.md
    python generate_audio.py podcast-script.md --output podcast.mp3
    python generate_audio.py podcast-script.md --voice zh-CN-YunxiNeural
"""

import argparse
import re
import sys
from pathlib import Path


def parse_markdown(text: str) -> str:
    """Strip markdown formatting and return plain text suitable for TTS.

    Removes: code fences, inline code, images, links (keeps link text),
    bold/italic markers, headers, blockquotes, horizontal rules, HTML tags.
    """
    # Remove code blocks (fenced)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove images ![alt](url) — drop entirely
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Remove links [text](url) — keep link text
    text = re.sub(r"\[([^\]]*?)\]\(.*?\)", r"\1", text)
    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}([^*]+?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+?)_{1,3}", r"\1", text)
    # Remove heading markers (keep the heading text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    # Remove fully blank lines that add no pause value (keep single newlines between paragraphs)
    cleaned = []
    for line in lines:
        if line:
            cleaned.append(line)
        elif cleaned and cleaned[-1] != "":
            cleaned.append("")
    # Join with spaces so TTS flows naturally; double-newline becomes a sentence break
    result = "\n".join(cleaned).strip()
    return result


def estimate_duration(text: str, chars_per_sec: float = 4.0) -> str:
    """Estimate audio duration from character count.

    Chinese TTS: ~4 characters per second is a reasonable estimate.
    English TTS: ~12-15 characters per second, but we use 4 as a conservative
    default since this targets Chinese.
    """
    char_count = len(text.replace("\n", "").replace(" ", ""))
    seconds = char_count / chars_per_sec
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}分{secs}秒（{char_count} 字符 @ {chars_per_sec} 字符/秒）"


async def text_to_speech(text: str, voice: str, output_path: str) -> None:
    """Convert text to MP3 audio using edge-tts."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="将播客脚本 Markdown 文件通过 edge-tts 转换为 MP3 音频。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例：
  python generate_audio.py podcast-script.md
  python generate_audio.py podcast-script.md --output podcast.mp3
  python generate_audio.py podcast-script.md --voice zh-CN-YunxiNeural

中文语音选项：
  zh-CN-XiaoxiaoNeural  女声，自然（默认）
  zh-CN-YunxiNeural     男声，自然
  zh-CN-YunyangNeural   男声，新闻播报风格
  zh-CN-XiaoyiNeural    女声，活泼
  zh-CN-YunjianNeural   男声，温暖年长
  zh-CN-XiaochenNeural  女声，活泼
  zh-CN-XiaohanNeural   女声，柔和

完整语音列表：edge-tts --list-voices | grep zh-CN
""",
    )
    parser.add_argument("input", type=str, nargs="?", help="播客脚本 Markdown 文件路径")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出 MP3 文件路径（默认：<输入文件名>.mp3）",
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="zh-CN-XiaoxiaoNeural",
        help="TTS 语音名称（默认：zh-CN-XiaoxiaoNeural）",
    )
    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：未找到输入文件：{input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.is_file():
        print(f"错误：不是有效文件：{input_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix(".mp3"))

    # Read and parse markdown
    raw_text = input_path.read_text(encoding="utf-8")
    plain_text = parse_markdown(raw_text)

    if not plain_text:
        print("解析后无可合成文本", file=sys.stderr)
        sys.exit(1)

    # Report stats
    print(f"输入: {input_path}")
    print(f"语音: {args.voice}")
    print(f"输出: {output_path}")
    print(f"时长: {estimate_duration(plain_text)}")
    print()

    # Check edge-tts availability
    try:
        import edge_tts  # noqa: F811
    except ImportError:
        print("错误：edge-tts 未安装。", file=sys.stderr)
        print("安装命令：pip install edge-tts", file=sys.stderr)
        print()
        print("edge-tts 是一个免费 Python 库，使用微软 Edge 的 TTS 引擎，")
        print("无需 API Key 即可将文本转为语音。")
        sys.exit(1)

    # Convert
    print("正在生成音频...")
    try:
        import asyncio

        asyncio.run(text_to_speech(plain_text, args.voice, output_path))
    except Exception as e:
        print(f"TTS 转换出错：{e}", file=sys.stderr)
        print()
        print("排查建议：")
        print("  1. 检查网络连接（edge-tts 需要联网访问微软 TTS 服务）")
        print("  2. 验证语音名称：edge-tts --list-voices | grep zh-CN")
        print("  3. 如果文本过长，请尝试分段合成")
        sys.exit(1)

    # Confirm
    out_file = Path(output_path)
    if out_file.exists():
        size_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"完成: {output_path}（{size_mb:.1f} MB）")
    else:
        print(f"错误：输出文件未生成：{output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
