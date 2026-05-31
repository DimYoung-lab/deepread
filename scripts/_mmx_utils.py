"""MiniMax Token Plan (mmx CLI) 共享工具函数。"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_mmx() -> Optional[str]:
    """查找 mmx CLI 可执行文件路径。"""
    found = shutil.which("mmx")
    if found:
        return found
    candidates = [
        Path.home() / "AppData" / "Roaming" / "npm" / "mmx.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "mmx",
        Path("/usr/local/bin/mmx"),
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


def run_mmx(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """运行 mmx CLI 命令，自动查找可执行文件路径。"""
    mmx_bin = find_mmx()
    if not mmx_bin:
        print("错误：未找到 mmx 命令。请先安装：npm install -g mmx-cli", file=sys.stderr)
        sys.exit(1)
    return subprocess.run([mmx_bin] + args, capture_output=True, text=True, timeout=timeout)
