#!/usr/bin/env python3
"""将播客脚本 Markdown 文件通过 MiniMax Speech API 转换为 MP3 音频。

使用 MiniMax T2A WebSocket API（speech-2.8 系列）进行中文语音合成。
支持多种语音、语速、音调控制。单次可处理最长 10,000 字符。

用法：
    python generate_audio.py podcast-script.md
    python generate_audio.py podcast-script.md --output podcast.mp3
    python generate_audio.py podcast-script.md --model speech-2.8-hd
    python generate_audio.py podcast-script.md --voice male-qn-qingse

API Key 设置（二选一）：
    - 环境变量：export MINIMAX_API_KEY=sk-api-...
    - 命令行参数：--api-key sk-api-...
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# MiniMax T2A WebSocket endpoint
T2A_WS_URL = "wss://api.minimaxi.com/ws/v1/t2a_v2"

# Default model and voice
DEFAULT_MODEL = "speech-2.8-turbo"
DEFAULT_VOICE = "male-qn-qingse"

# Chinese chars per second estimate
CHARS_PER_SECOND = 4.0

# Available models
AVAILABLE_MODELS = [
    "speech-2.8-turbo",   # 极速版，自然逼真
    "speech-2.8-hd",      # 高清版，情绪渲染 + 语气词
    "speech-2.6-turbo",
    "speech-2.6-hd",
    "speech-02-turbo",
    "speech-02-hd",
]

# Chinese voice options (confirmed working)
VOICE_OPTIONS = [
    "male-qn-qingse",         # 男声-青涩（默认）
    "female-shaonv",           # 女声-少女
    "female-yousheng",         # 女声-优声
    "male-wenhao",             # 男声-文豪
    "presenter_male",          # 男声-主持人
    "presenter_female",        # 女声-主持人
    "audiobook_male_1",        # 有声书男声1
    "audiobook_female_1",      # 有声书女声1
    "clever_boy",              # 聪明男孩
    "cute_boy",                # 可爱男孩
    "humorous_male",           # 幽默男声
]


# ---------------------------------------------------------------------------
# Markdown parsing (TTS-engine-agnostic)
# ---------------------------------------------------------------------------

def parse_markdown(raw: str) -> str:
    """从 Markdown 播客脚本中提取纯文本，去除所有 Markdown 格式标记。"""
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
    # 去除【】标记
    text = re.sub(r"【[^】]*】", "", text)

    # 折叠多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)
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
# MiniMax T2A WebSocket API
# ---------------------------------------------------------------------------

async def minimax_tts(
    text: str,
    output_path: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    voice_id: str = DEFAULT_VOICE,
    speed: float = 1.0,
    vol: float = 1.0,
    pitch: float = 0.0,
    sample_rate: int = 32000,
    bitrate: int = 128000,
) -> None:
    """通过 MiniMax T2A WebSocket API 将文本转为 MP3 音频。"""
    import websockets

    ssl_context = ssl.create_default_context()
    headers = {"Authorization": f"Bearer {api_key}"}

    all_audio: list[bytes] = []
    started = False

    async with websockets.connect(
        T2A_WS_URL,
        additional_headers=headers,
        ssl=ssl_context,
        ping_interval=30,
        ping_timeout=10,
    ) as ws:
        # 1. 等待连接确认
        resp = json.loads(await ws.recv())
        if resp.get("event") != "connected_success":
            raise RuntimeError(f"WebSocket 连接失败：{resp}")

        # 2. 发送 task_start
        # NOTE: speed/vol/pitch must be Python numbers (int where possible)
        # because the API rejects float-format values like 1.0
        task_start = {
            "event": "task_start",
            "model": model,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": int(speed) if speed == int(speed) else speed,
                "vol": int(vol) if vol == int(vol) else vol,
                "pitch": int(pitch) if pitch == int(pitch) else pitch,
            },
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": "mp3",
                "channel": 1,
            },
        }
        await ws.send(json.dumps(task_start))

        # 3. 等待 task_started 确认
        resp = json.loads(await ws.recv())
        if resp.get("event") != "task_started":
            raise RuntimeError(f"task_start 失败：{resp}")

        # 4. 发送文本
        task_continue = {
            "event": "task_continue",
            "text": text,
        }
        await ws.send(json.dumps(task_continue))

        # 5. 接收音频数据
        while True:
            resp = json.loads(await ws.recv())
            event_type = resp.get("event", "")

            if "data" in resp and resp["data"].get("audio"):
                audio_hex = resp["data"]["audio"]
                audio_bytes = bytes.fromhex(audio_hex)
                all_audio.append(audio_bytes)

            if resp.get("is_final", False):
                break

            # 处理错误事件
            if event_type == "error":
                raise RuntimeError(f"MiniMax API 错误：{resp}")

        # 6. 发送 task_finish
        await ws.send(json.dumps({"event": "task_finish"}))

    # 合并并写入 MP3
    combined = b"".join(all_audio)
    Path(output_path).write_bytes(combined)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def get_api_key(cli_key: Optional[str]) -> str:
    """获取 API Key（优先 CLI 参数，其次环境变量）。"""
    if cli_key:
        return cli_key
    env_key = os.environ.get("MINIMAX_API_KEY", "")
    if env_key:
        return env_key
    print("错误：未提供 MiniMax API Key。", file=sys.stderr)
    print("请通过以下方式之一提供：", file=sys.stderr)
    print("  1. 环境变量：export MINIMAX_API_KEY=sk-api-...", file=sys.stderr)
    print("  2. 命令行参数：--api-key sk-api-...", file=sys.stderr)
    sys.exit(1)


def build_argparser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="将播客脚本 Markdown 文件通过 MiniMax Speech API 转换为 MP3 音频。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""示例：
  python generate_audio.py podcast-script.md
  python generate_audio.py podcast-script.md --model speech-2.8-hd
  python generate_audio.py podcast-script.md --voice male-qn-qingse

可用模型：
  speech-2.8-turbo  极速版，自然逼真（默认）
  speech-2.8-hd     高清版，情绪渲染融合语气词
  speech-2.6-turbo  速度优先，适合聊天/数字人
  speech-2.6-hd     超低延时，高自然度
  speech-02-hd      出色韵律与稳定性，复刻相似度高

可用语音（中文）：
  male-qn-qingse       男声-青涩（默认）
  female-shaonv         女声-少女
  female-yousheng       女声-优声
  male-wenhao           男声-文豪
  presenter_male        男声-主持人
  presenter_female      女声-主持人
  audiobook_male_1      有声书男声
  audiobook_female_1    有声书女声

API Key 设置：
  export MINIMAX_API_KEY=sk-api-...

文档：https://platform.minimaxi.com/docs/guides/speech-t2a-websocket
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
        "--model", "-m",
        metavar="MODEL",
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"MiniMax 模型名称（默认：{DEFAULT_MODEL}）。",
    )
    parser.add_argument(
        "--voice", "-v",
        metavar="VOICE_ID",
        default=DEFAULT_VOICE,
        help=f"语音 ID（默认：{DEFAULT_VOICE}）。",
    )
    parser.add_argument(
        "--speed",
        metavar="FLOAT",
        type=float,
        default=1.0,
        help="语速倍率（默认：1.0，范围 0.5–2.0）。",
    )
    parser.add_argument(
        "--vol",
        metavar="FLOAT",
        type=float,
        default=1.0,
        help="音量倍率（默认：1.0）。",
    )
    parser.add_argument(
        "--pitch",
        metavar="FLOAT",
        type=float,
        default=0.0,
        help="音调偏移（默认：0.0，范围 -12–12）。",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        default=None,
        help="MiniMax API Key（也可通过环境变量 MINIMAX_API_KEY 设置）。",
    )
    parser.add_argument(
        "--sample-rate",
        metavar="HZ",
        type=int,
        default=32000,
        help="采样率（默认：32000）。",
    )
    parser.add_argument(
        "--bitrate",
        metavar="BPS",
        type=int,
        default=128000,
        help="比特率（默认：128000）。",
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

    # --- 获取 API Key ---
    api_key = get_api_key(args.api_key)

    # --- 确定输出路径 ---
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix(".mp3"))

    # --- 读取并解析 Markdown ---
    raw_text = input_path.read_text(encoding="utf-8")
    plain_text = parse_markdown(raw_text)

    if not plain_text:
        print("错误：解析 Markdown 后未找到可合成文本。", file=sys.stderr)
        sys.exit(1)

    # 检查文本长度
    if len(plain_text) > 10000:
        print(f"警告：文本过长（{len(plain_text)} 字符），MiniMax 单次最多 10,000 字符。", file=sys.stderr)
        print("将截断到前 10,000 字符。", file=sys.stderr)
        plain_text = plain_text[:10000]

    # --- 报告统计信息 ---
    print(f"输入文件：  {input_path}")
    print(f"模型：      {args.model}")
    print(f"语音：      {args.voice}")
    print(f"输出文件：  {output_path}")
    print(f"预计时长：  {estimate_duration(plain_text)}")
    print()

    # --- TTS 合成 ---
    try:
        print("正在连接 MiniMax API...")
        t0 = time.time()
        asyncio.run(minimax_tts(
            text=plain_text,
            output_path=output_path,
            api_key=api_key,
            model=args.model,
            voice_id=args.voice,
            speed=args.speed,
            vol=args.vol,
            pitch=args.pitch,
            sample_rate=args.sample_rate,
            bitrate=args.bitrate,
        ))
        elapsed = time.time() - t0
        print(f"合成完成（耗时 {elapsed:.1f} 秒）")
    except Exception as exc:
        print(f"TTS 转换出错：{exc}", file=sys.stderr)
        print(file=sys.stderr)
        print("排查建议：", file=sys.stderr)
        print("  1. 检查 API Key 是否正确", file=sys.stderr)
        print("  2. 检查网络连接（需要访问 api.minimaxi.com）", file=sys.stderr)
        print("  3. 检查文本长度是否超过 10,000 字符限制", file=sys.stderr)
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
