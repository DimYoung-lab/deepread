#!/usr/bin/env python3
"""Render styled PDF reports from Markdown output files.

Converts Markdown to HTML via markdown-it-py, wraps in a Jinja2 HTML
template with premium print CSS, and renders to PDF via Playwright
headless Chromium.

Designed for the interview-based-learning skill's three Markdown outputs:
  - Deep-dive report (--type report)      — cover page + full report
  - TL;DR summary     (--type tldr)       — compact layout
  - Social media post (--type social)     — narrative article layout

Usage:
    python generate_pdf.py report-guestname-YYYYMMDD.md
    python generate_pdf.py report-guestname-YYYYMMDD.md --type report -o report.pdf
    python generate_pdf.py tldr-guestname-YYYYMMDD.md --type tldr -o tldr.pdf
    python generate_pdf.py social-guestname-YYYYMMDD.md --type social
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Markdown → HTML conversion
# ---------------------------------------------------------------------------

def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML using markdown-it-py with GFM support.

    Enables table, strikethrough, and task list extensions for full
    coverage of the deep-dive report's markdown constructs.
    """
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark", {"breaks": True, "html": True})
    md.enable("table")
    md.enable("strikethrough")

    return md.render(md_text)


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_metadata(md_text: str) -> dict[str, str]:
    """Extract guest name, show name, host, date, duration from markdown.

    Handles three formats:
      - Deep report:  # GUEST on SHOW: 深度报告  /  *Guest: ..., Host: ..., Duration: ..., Date: ..., Show: ...*
      - TL;DR:        # GUEST × HOST: TL;DR       /  *Guest: ..., Duration: ..., Date: ...*
      - Social post:  # TITLE                      /  > author attribution line
    """
    meta: dict[str, str] = {
        "title": "",
        "title_short": "",
        "guest_name": "",
        "show_name": "",
        "host": "",
        "date": "",
        "duration": "",
    }

    lines = md_text.strip().split("\n")

    # --- Title (first h1) ---
    for line in lines[:5]:
        h1_match = re.match(r"^#\s+(.+)$", line)
        if h1_match:
            meta["title"] = h1_match.group(1).strip()
            break

    # --- Metadata line (italic line with pipe-separated fields) ---
    # Pattern: *Guest: ... | Host: ... | Duration: ... | Date: ... | Show: ...*
    for line in lines[:10]:
        stripped = line.strip()
        if not stripped.startswith("*") and not stripped.startswith(">"):
            continue

        # Remove leading/trailing asterisks and blockquote markers
        cleaned = re.sub(r"^[>\s]*\*?\s*", "", stripped)
        cleaned = re.sub(r"\s*\*?\s*$", "", cleaned)

        # Extract fields
        guest_match = re.search(r"Guest:\s*(.+?)(?:\s*\||$)", cleaned)
        host_match = re.search(r"Host:\s*(.+?)(?:\s*\||$)", cleaned)
        duration_match = re.search(r"Duration:\s*(.+?)(?:\s*\||$)", cleaned)
        date_match = re.search(r"Date:\s*(.+?)(?:\s*\||$)", cleaned)
        show_match = re.search(r"Show:\s*(.+?)(?:\s*\||$)", cleaned)
        episode_match = re.search(r"Episode:\s*(.+?)(?:\s*\||$)", cleaned)

        if guest_match:
            guest_raw = guest_match.group(1).strip()
            # Extract name before first comma or parenthesis with English name
            name_only = re.sub(r"\s*\(.*?\).*", "", guest_raw)
            name_only = re.sub(r",.*", "", name_only).strip()
            meta["guest_name"] = name_only if name_only else guest_raw

        if host_match:
            meta["host"] = host_match.group(1).strip()

        if duration_match:
            meta["duration"] = duration_match.group(1).strip()

        if date_match:
            meta["date"] = date_match.group(1).strip()

        if show_match:
            meta["show_name"] = show_match.group(1).strip()
        elif episode_match:
            meta["show_name"] = episode_match.group(1).strip()

        # If we found at least one field, this was the metadata line
        if any([guest_match, host_match, duration_match, date_match]):
            break

    # --- Fallback: derive guest/show from title ---
    if not meta["guest_name"] and meta["title"]:
        # Pattern: "GUEST on SHOW: ..." or "GUEST × HOST: ..."
        title_match = re.match(r"^(.+?)\s+(?:on|×)\s+(.+?)\s*[:：]", meta["title"])
        if title_match:
            meta["guest_name"] = title_match.group(1).strip()
            meta["show_name"] = title_match.group(2).strip()
        else:
            # Use full title as guest_name fallback
            meta["guest_name"] = meta["title"]

    # --- Title short (for running headers) ---
    if meta["guest_name"]:
        meta["title_short"] = meta["guest_name"]
    else:
        meta["title_short"] = meta["title"][:30] if meta["title"] else "Report"

    return meta


# ---------------------------------------------------------------------------
# HTML document assembly
# ---------------------------------------------------------------------------

def build_html_document(
    body_html: str,
    metadata: dict[str, str],
    css: str,
    template_str: str,
) -> str:
    """Render the Jinja2 template with body HTML, metadata, and CSS."""
    from jinja2 import Template

    template = Template(template_str)
    return template.render(
        title=metadata.get("title", "Report"),
        title_short=metadata.get("title_short", "Report"),
        guest_name=metadata.get("guest_name", ""),
        show_name=metadata.get("show_name", ""),
        host=metadata.get("host", ""),
        date=metadata.get("date", ""),
        duration=metadata.get("duration", ""),
        body_html=body_html,
        css=css,
    )


# ---------------------------------------------------------------------------
# PDF rendering via Playwright
# ---------------------------------------------------------------------------

def html_to_pdf(html: str, output_path: str, page_size: str = "A4") -> None:
    """Write HTML to temp file, render to PDF via Playwright headless Chromium.

    Uses Playwright's page.pdf() with print backgrounds enabled so the
    cream + burgundy color scheme is preserved in the output.
    """
    from playwright.sync_api import sync_playwright

    # Write HTML to a temp file — file:// URLs are more reliable for
    # CSS @page support than page.set_content().
    tmp = None
    tmp_path: Optional[str] = None
    try:
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".html",
            encoding="utf-8",
            delete=False,
        )
        tmp.write(html)
        tmp.flush()
        tmp_path = tmp.name
        tmp.close()
        tmp = None

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the temp HTML file
            page.goto(f"file:///{tmp_path.replace(chr(92), '/')}", wait_until="networkidle")

            # Wait for any fonts/images to settle
            page.wait_for_timeout(500)

            # Render PDF — Playwright's `format` controls page size.
            # Margins are set in CSS @page rules (not here) so that
            # @page :first can use margin:0 for full-bleed cover.
            page.pdf(
                path=output_path,
                format=page_size,
                print_background=True,
                display_header_footer=False,
            )

            browser.close()

    finally:
        # Clean up temp file
        if tmp is not None:
            try:
                tmp.close()
            except Exception:
                pass
        if tmp_path:
            tmp_file = Path(tmp_path)
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    # Non-critical: temp file will be cleaned by OS eventually
                    pass


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def load_template_and_css(template_dir: str, format_type: str) -> tuple[str, str]:
    """Load the Jinja2 template and CSS from the template directory.

    Returns (template_string, css_string).
    """
    base = Path(template_dir)

    # Map format type to template filename
    template_map = {
        "report": "report-wrapper.html.j2",
        "tldr": "tldr-wrapper.html.j2",
        "social": "social-wrapper.html.j2",
    }
    template_name = template_map.get(format_type, "report-wrapper.html.j2")
    template_path = base / template_name
    css_path = base / "pdf-style.css"

    missing: list[str] = []
    for p in (template_path, css_path):
        if not p.is_file():
            missing.append(str(p))
    if missing:
        raise FileNotFoundError(
            f"错误：未找到模板文件：{', '.join(missing)}"
        )

    template_str = template_path.read_text(encoding="utf-8")
    css_str = css_path.read_text(encoding="utf-8")

    return template_str, css_str


# ---------------------------------------------------------------------------
# Output path resolution
# ---------------------------------------------------------------------------

def resolve_output_path(input_path: str, output_arg: Optional[str]) -> str:
    """Determine the output PDF path.

    If --output is provided, use it directly.
    Otherwise, place the PDF in a sibling `pdf/` directory alongside
    the input (which is typically in `reports/`).
    """
    if output_arg:
        return output_arg
    p = Path(input_path)
    parent = p.parent
    # If input is in a `reports/` dir, write to sibling `pdf/` dir
    if parent.name == "reports":
        pdf_dir = parent.parent / "pdf"
    else:
        pdf_dir = parent
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return str(pdf_dir / p.with_suffix(".pdf").name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="将 Markdown 报告渲染为带排版的精美 PDF 文件。",
    )
    parser.add_argument(
        "input_md",
        metavar="INPUT_MD",
        help="输入的 Markdown 文件路径（如 report-guest-YYYYMMDD.md）。",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        default=None,
        help="输出 PDF 文件路径，默认与输入同名（.pdf 后缀）。",
    )
    parser.add_argument(
        "--type", "-t",
        metavar="TYPE",
        default="report",
        choices=["report", "tldr", "social"],
        help="输出格式类型：report（含封面和页眉）、tldr（紧凑版）、social（叙事版），默认 report。",
    )
    parser.add_argument(
        "--page-size",
        metavar="SIZE",
        default="A4",
        choices=["A4", "Letter", "A3", "A5"],
        help="PDF 页面尺寸，默认 A4。",
    )
    parser.add_argument(
        "--template-dir",
        metavar="DIR",
        default=None,
        help="PDF 模板目录路径，默认为脚本同级的 ../assets/pdf-templates/。",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point."""
    parser = build_argparser()
    args = parser.parse_args(argv)

    # --- Resolve paths ---
    input_path = args.input_md
    if not Path(input_path).is_file():
        print(f"错误：未找到输入文件：{input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = resolve_output_path(input_path, args.output)

    # Resolve template directory
    if args.template_dir:
        template_dir = args.template_dir
    else:
        script_dir = Path(__file__).resolve().parent
        template_dir = str(script_dir.parent / "assets" / "pdf-templates")

    # --- Load template and CSS ---
    try:
        template_str, css_str = load_template_and_css(template_dir, args.type)
    except FileNotFoundError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        sys.exit(1)

    # --- Read markdown ---
    try:
        md_text = Path(input_path).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"读取文件出错 {input_path}：{exc}", file=sys.stderr)
        sys.exit(1)

    # --- Convert markdown to HTML ---
    body_html = md_to_html(md_text)

    # --- Extract metadata ---
    metadata = extract_metadata(md_text)

    # --- Assemble HTML document ---
    try:
        html = build_html_document(body_html, metadata, css_str, template_str)
    except Exception as exc:
        print(f"构建 HTML 文档出错：{exc}", file=sys.stderr)
        sys.exit(2)

    # --- Render to PDF ---
    try:
        html_to_pdf(html, output_path, args.page_size)
    except Exception as exc:
        print(f"渲染 PDF 出错：{exc}", file=sys.stderr)
        sys.exit(2)

    print(f"PDF 已写入：{Path(output_path).resolve()}")


if __name__ == "__main__":
    main()
