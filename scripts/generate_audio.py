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
    return f"{minutes}m {secs}s ({char_count} chars @ {chars_per_sec} chars/sec)"


async def text_to_speech(text: str, voice: str, output_path: str) -> None:
    """Convert text to MP3 audio using edge-tts."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a podcast script markdown file to MP3 audio via edge-tts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python generate_audio.py podcast-script.md
  python generate_audio.py podcast-script.md --output podcast.mp3
  python generate_audio.py podcast-script.md --voice zh-CN-YunxiNeural

Voice options (Chinese):
  zh-CN-XiaoxiaoNeural  Female, natural (default)
  zh-CN-YunxiNeural     Male, natural
  zh-CN-YunyangNeural   Male, news-anchor style
  zh-CN-XiaoyiNeural    Female, lively
  zh-CN-YunjianNeural   Male, older, warm
  zh-CN-XiaochenNeural  Female, lively
  zh-CN-XiaohanNeural   Female, soft

Full voice list: edge-tts --list-voices | grep zh-CN
""",
    )
    parser.add_argument("input", type=str, nargs="?", help="Path to podcast script markdown file")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output MP3 file path (default: <input-stem>.mp3)",
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="zh-CN-XiaoxiaoNeural",
        help="TTS voice name (default: zh-CN-XiaoxiaoNeural)",
    )
    args = parser.parse_args()

    if args.input is None:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)
    if not input_path.is_file():
        print(f"Error: not a file: {input_path}")
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
        print("Error: no text content found after parsing markdown.")
        sys.exit(1)

    # Report stats
    print(f"Input:      {input_path}")
    print(f"Voice:      {args.voice}")
    print(f"Output:     {output_path}")
    print(f"Duration:   {estimate_duration(plain_text)}")
    print()

    # Check edge-tts availability
    try:
        import edge_tts  # noqa: F811
    except ImportError:
        print("Error: edge-tts is not installed.")
        print("Install it with:  pip install edge-tts")
        print()
        print("edge-tts is a free Python library that uses Microsoft Edge's")
        print("TTS engine to convert text to speech without API keys.")
        sys.exit(1)

    # Convert
    print("Generating audio...")
    try:
        import asyncio

        asyncio.run(text_to_speech(plain_text, args.voice, output_path))
    except Exception as e:
        print(f"Error during TTS conversion: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check your internet connection (edge-tts requires network access)")
        print("  2. Verify the voice name: edge-tts --list-voices | grep zh-CN")
        print("  3. If the text is very long, try splitting it into smaller chunks")
        sys.exit(1)

    # Confirm
    out_file = Path(output_path)
    if out_file.exists():
        size_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"Done: {output_path} ({size_mb:.1f} MB)")
    else:
        print(f"Error: output file was not created: {output_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
