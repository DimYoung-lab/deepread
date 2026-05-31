#!/usr/bin/env python3
"""将播客脚本 Markdown 文件通过 CosyVoice 3.0 转换为 MP3 音频。

使用阿里达摩院 FunAudioLLM CosyVoice 3.0 模型进行中文语音合成。
支持自然语言指令控制语速、情绪和风格。长文本自动分段合成后拼接。

用法：
    python generate_audio.py podcast-script.md
    python generate_audio.py podcast-script.md --output podcast.mp3
    python generate_audio.py podcast-script.md --instruct "用温柔的声音说"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default CosyVoice paths (relative to this script's location)
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = str(SCRIPT_DIR.parent.parent / "CosyVoice" / "pretrained_models" / "Fun-CosyVoice3-0.5B")
DEFAULT_REF_AUDIO = str(SCRIPT_DIR.parent.parent / "CosyVoice" / "asset" / "zero_shot_prompt.wav")
DEFAULT_COSYVOICE_REPO = str(SCRIPT_DIR.parent.parent / "CosyVoice")

# ffmpeg paths to try (for pydub WAV→MP3 conversion)
_FFMPEG_CANDIDATES = [
    # winget install location
    os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    ),
    # common fallback locations
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
]


def _ensure_ffmpeg() -> None:
    """Ensure ffmpeg is available in PATH for pydub MP3 export."""
    import shutil

    # Check if already in PATH
    if shutil.which("ffmpeg"):
        return

    # Search known locations
    for base in _FFMPEG_CANDIDATES:
        if not os.path.isdir(base):
            continue
        for root, dirs, _ in os.walk(base):
            if "ffmpeg.exe" in os.listdir(root) if os.path.isdir(root) else False:
                continue
            ffmpeg_dir = os.path.join(root, "bin") if "bin" in dirs else root
            ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
            if os.path.isfile(ffmpeg_exe):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                return

    # Not found — pydub will warn but may still fail
    pass

# Default TTS instruction — natural podcast narrator style in Chinese
DEFAULT_INSTRUCT = (
    "You are a helpful assistant. "
    "用自然平和的语气，像播客主持人一样讲述，语速适中，声音温暖清晰。"
    "<|endofprompt|>"
)

# Chunking: CosyVoice works best with ~150 Chinese chars per inference
DEFAULT_CHUNK_SIZE = 150

# Prompt text that pairs with the reference audio
PROMPT_TEXT = "You are a helpful assistant.<|endofprompt|>希望你以后能够做的比我还好呦。"

# Chinese chars-per-second for duration estimation
CHARS_PER_SECOND = 4.0


# ---------------------------------------------------------------------------
# Markdown parsing (TTS-engine-agnostic)
# ---------------------------------------------------------------------------

def parse_markdown(raw: str) -> str:
    """从 Markdown 播客脚本中提取纯文本，去除所有 Markdown 格式标记。

    去除的内容：
    - 代码块（```...```）和行内代码（`...`）
    - 图片（![...](...)）和链接（[...](...)——保留文字）
    - 加粗/斜体标记
    - 标题标记（#）
    - 引用标记（>）
    - 水平线（---）
    - HTML 标签
    - === 分隔符和舞台指示
    """
    text = raw

    # 去除代码块
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # 去除行内代码
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # 去除图片
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # 去除链接（保留文字）
    text = re.sub(r"\[([^\]]*)\]\(.*?\)", r"\1", text)
    # 去除加粗/斜体
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # 去除标题标记
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # 去除引用标记
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # 去除水平线
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 去除 === 分隔符和舞台指示行
    text = re.sub(r"^={3,}.*$", "", text, flags=re.MULTILINE)
    # 去除【】标记（中文舞台指示）
    text = re.sub(r"【[^】]*】", "", text)

    # 折叠多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 去除行首行尾空白
    text = text.strip()

    return text


def estimate_duration(text: str) -> str:
    """估算纯文本的朗读时长。"""
    chars = len(text.replace("\n", "").replace(" ", ""))
    seconds = chars / CHARS_PER_SECOND
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}分{secs}秒（{chars} 字符，按 {CHARS_PER_SECOND} 字/秒估算）"


# ---------------------------------------------------------------------------
# Text chunking for CosyVoice
# ---------------------------------------------------------------------------

def split_text_for_tts(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """将长文本按句子边界拆分为适合 CosyVoice 推理的短片段。

    CosyVoice 3.0 在 ~100-200 字符范围内效果最佳。
    拆分策略：优先在句号、问号、感叹号处断开。
    """
    # 按句子分隔符拆分
    sentences = re.split(r"(?<=[。！？.!?，,；;：:\n])", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks: list[str] = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) <= chunk_size:
            current += sent
        else:
            if current:
                chunks.append(current)
            # 如果单句超过 chunk_size，强制按字符切分
            if len(sent) > chunk_size:
                for i in range(0, len(sent), chunk_size):
                    chunks.append(sent[i:i + chunk_size])
                current = ""
            else:
                current = sent

    if current:
        chunks.append(current)

    return chunks


# ---------------------------------------------------------------------------
# CosyVoice TTS inference
# ---------------------------------------------------------------------------

def load_cosyvoice(model_dir: str, repo_dir: str):
    """加载 CosyVoice 模型。

    返回 (cosyvoice_instance, sample_rate)。
    """
    # 将 CosyVoice 仓库和第三方依赖加入 sys.path
    cosyvoice_path = Path(repo_dir)
    if str(cosyvoice_path) not in sys.path:
        sys.path.insert(0, str(cosyvoice_path))
    matcha_path = cosyvoice_path / "third_party" / "Matcha-TTS"
    if str(matcha_path) not in sys.path:
        sys.path.insert(0, str(matcha_path))

    from cosyvoice.cli.cosyvoice import AutoModel

    cosyvoice = AutoModel(model_dir=model_dir)
    return cosyvoice, cosyvoice.sample_rate


def synthesize_chunk(
    cosyvoice,
    text: str,
    instruct: str,
    ref_audio: str,
    prompt_text: str,
    output_path: str,
) -> None:
    """用 CosyVoice 合成单个文本片段为 WAV 文件。"""
    import torchaudio

    for i, result in enumerate(cosyvoice.inference_instruct2(
        text,
        instruct,
        ref_audio,
        stream=False,
    )):
        torchaudio.save(output_path, result["tts_speech"], cosyvoice.sample_rate)
        break  # 只取第一个结果


def text_to_speech(
    text: str,
    output_path: str,
    model_dir: str = DEFAULT_MODEL_DIR,
    repo_dir: str = DEFAULT_COSYVOICE_REPO,
    ref_audio: str = DEFAULT_REF_AUDIO,
    instruct: str = DEFAULT_INSTRUCT,
    prompt_text: str = PROMPT_TEXT,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    """将纯文本通过 CosyVoice 转换为 MP3 音频。

    自动处理长文本分段、逐段合成、WAV 拼接、MP3 转换。
    """
    # 加载模型（仅加载一次）
    print("正在加载 CosyVoice 模型...")
    cosyvoice, sample_rate = load_cosyvoice(model_dir, repo_dir)
    print("模型加载完成。")

    # 拆分文本
    chunks = split_text_for_tts(text, chunk_size)
    total = len(chunks)
    print(f"文本已拆分为 {total} 个片段（每段 ≤ {chunk_size} 字符）")

    # 逐段合成
    tmp_dir = tempfile.mkdtemp(prefix="cosyvoice_chunks_")
    wav_paths: list[str] = []
    try:
        for idx, chunk in enumerate(chunks, 1):
            wav_path = os.path.join(tmp_dir, f"chunk_{idx:04d}.wav")
            print(f"  合成第 {idx}/{total} 段（{len(chunk)} 字符）...", end=" ", flush=True)
            synthesize_chunk(
                cosyvoice, chunk, instruct, ref_audio, prompt_text, wav_path,
            )
            wav_paths.append(wav_path)
            print("完成")

        # 拼接 WAV → MP3
        print(f"正在拼接 {len(wav_paths)} 个音频片段...")
        concat_wavs_to_mp3(wav_paths, output_path)
        print(f"音频已拼接完成。")

    finally:
        # 清理临时 WAV 文件
        for p in wav_paths:
            try:
                os.unlink(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass


def concat_wavs_to_mp3(wav_paths: list[str], output_path: str) -> None:
    """将多个 WAV 文件拼接为单个 MP3 文件。"""
    _ensure_ffmpeg()
    from pydub import AudioSegment

    combined = AudioSegment.empty()
    for wav_path in wav_paths:
        segment = AudioSegment.from_wav(wav_path)
        combined += segment

    # 导出为 MP3（需要 ffmpeg）
    combined.export(output_path, format="mp3", bitrate="192k")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="将播客脚本 Markdown 文件通过 CosyVoice 3.0 转换为 MP3 音频。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  python generate_audio.py podcast-script.md
  python generate_audio.py podcast-script.md --output podcast.mp3
  python generate_audio.py podcast-script.md --instruct "用温柔的声音说"

CosyVoice 3.0 基于阿里达摩院 FunAudioLLM，支持：
  - 自然语言指令控制语速、情绪、风格
  - 18+ 中文方言
  - 完全离线推理（需 GPU，约 2-4 GB 显存）
  - 中文 CER 0.81%（开源 SOTA）

首次使用需要先下载模型（约 10 GB）：
  python -c "from modelscope import snapshot_download; snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir='pretrained_models/Fun-CosyVoice3-0.5B')"
""",
    )
    parser.add_argument(
        "input",
        metavar="INPUT_MD",
        help="输入的播客脚本 Markdown 文件路径。",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        default=None,
        help="输出 MP3 文件路径，默认与输入同名（.mp3 后缀）。",
    )
    parser.add_argument(
        "--instruct", "-i",
        metavar="TEXT",
        default=DEFAULT_INSTRUCT,
        help="CosyVoice 自然语言指令，用于控制语音风格。"
             "例如：'用温柔的声音说'、'请用严肃的语气'、'语速放慢一点'。",
    )
    parser.add_argument(
        "--model-dir",
        metavar="DIR",
        default=DEFAULT_MODEL_DIR,
        help=f"CosyVoice 模型权重目录（默认：{DEFAULT_MODEL_DIR}）。",
    )
    parser.add_argument(
        "--ref-audio",
        metavar="PATH",
        default=DEFAULT_REF_AUDIO,
        help="参考音频文件路径，用于音色预设。",
    )
    parser.add_argument(
        "--chunk-size",
        metavar="N",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"每段最大字符数（默认：{DEFAULT_CHUNK_SIZE}）。",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """入口函数。"""
    parser = build_argparser()
    args = parser.parse_args(argv)

    # --- 验证输入 ---
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：未找到输入文件：{input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.is_file():
        print(f"错误：不是有效文件：{input_path}", file=sys.stderr)
        sys.exit(1)

    # --- 确定输出路径 ---
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix(".mp3"))

    # --- 验证模型 ---
    model_dir = Path(args.model_dir)
    if not model_dir.exists():
        print(f"错误：CosyVoice 模型目录不存在：{model_dir}", file=sys.stderr)
        print(f"请先下载模型：", file=sys.stderr)
        print(f"  python -c \"from modelscope import snapshot_download; snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir='{args.model_dir}')\"", file=sys.stderr)
        sys.exit(1)

    ref_audio = Path(args.ref_audio)
    if not ref_audio.exists():
        print(f"错误：参考音频文件不存在：{ref_audio}", file=sys.stderr)
        sys.exit(1)

    # --- 读取并解析 Markdown ---
    raw_text = input_path.read_text(encoding="utf-8")
    plain_text = parse_markdown(raw_text)

    if not plain_text:
        print("错误：解析 Markdown 后未找到可合成文本。", file=sys.stderr)
        sys.exit(1)

    # --- 报告统计信息 ---
    print(f"输入文件：  {input_path}")
    print(f"指令：      {args.instruct[:60]}...")
    print(f"输出文件：  {output_path}")
    print(f"预计时长：  {estimate_duration(plain_text)}")
    print()

    # --- TTS 合成 ---
    try:
        text_to_speech(
            text=plain_text,
            output_path=output_path,
            model_dir=str(model_dir),
            ref_audio=str(ref_audio),
            instruct=args.instruct,
            chunk_size=args.chunk_size,
        )
    except Exception as exc:
        print(f"TTS 转换出错：{exc}", file=sys.stderr)
        print(file=sys.stderr)
        print("排查建议：", file=sys.stderr)
        print("  1. 检查 GPU 是否可用：python -c \"import torch; print(torch.cuda.is_available())\"", file=sys.stderr)
        print("  2. 检查模型是否完整下载（约 10 GB）", file=sys.stderr)
        print("  3. 检查参考音频文件是否存在", file=sys.stderr)
        print("  4. 如果显存不足，尝试减小 --chunk-size 参数", file=sys.stderr)
        sys.exit(1)

    # --- 确认输出 ---
    out_file = Path(output_path)
    if out_file.exists():
        size_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"完成：{output_path}（{size_mb:.1f} MB）")
    else:
        print(f"错误：输出文件未生成：{output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
