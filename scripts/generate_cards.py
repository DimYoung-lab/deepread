#!/usr/bin/env python3
"""Generate a self-contained interactive learning cards HTML page from visual_content.json.

Reads visual_content.json (produced by Stage 4.5 visual synthesis) and renders
a mobile-first, card-based learning experience. Each cross-cutting theme becomes
a swipeable card with progressive disclosure: claim → narrative → quote → evidence.

Usage:
    python generate_cards.py visual_content.json
    python generate_cards.py visual_content.json --output cards.html
    python generate_cards.py visual_content.json -o cards.html --template-dir assets/cards-template/
    python generate_cards.py visual_content.json --knowledge knowledge.json
"""

from __future__ import annotations

import argparse
import html as _html
import json
import sys
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def esc(text: str, quote: bool = True) -> str:
    """HTML-escape a string."""
    return _html.escape(text, quote=quote)


def timestamp_badge(ts: str) -> str:
    """Render a clickable timestamp span."""
    e = esc(ts)
    return f'<span class="timestamp-badge" data-time="{e}">{e}</span>'


# ---------------------------------------------------------------------------
# Hero Card Builder
# ---------------------------------------------------------------------------


def build_hero_card(data: JSON) -> str:
    """Build the hero/cover card with core thesis and call-to-action."""
    meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]

    thesis = esc(meta.get("core_thesis", ""))
    stats = meta.get("stats", {})
    dur = esc(str(stats.get("duration_formatted", "")))
    theme_n = str(stats.get("theme_count", "7"))

    lines: list[str] = []
    lines.append('<article class="card card-hero" id="card-0">')

    # Badge
    lines.append('  <div class="card-badge">Learning Cards</div>')

    # Title
    lines.append(f'  <h1 class="card-title">{thesis}</h1>')

    # Subtitle
    lines.append(
        f'  <p class="card-subtitle">'
        f'一场{dur}的深度对话，浓缩为{theme_n}个核心洞察'
        f'</p>'
    )

    # Meta
    meta_parts: list[str] = []
    guest_info = _get_guest_name(data)
    if guest_info:
        meta_parts.append(f"<span>🎙 {esc(guest_info)}</span>")
    lines.append(f'  <div class="card-meta">{" · ".join(meta_parts) if meta_parts else ""}</div>')

    # Actions
    lines.append('  <div class="hero-actions">')
    lines.append('    <button class="btn btn-primary">开始学习 →</button>')
    lines.append('    <a href="#" class="btn btn-secondary" data-goto="closing">跳到总结</a>')
    lines.append('  </div>')

    lines.append('</article>')
    return "\n".join(lines)


def _get_guest_name(data: JSON) -> str:
    """Extract guest name from visual_content or knowledge metadata."""
    meta = data.get("meta", data.get("metadata", {}))
    if isinstance(meta, dict):
        guest = meta.get("guest", "")
        if isinstance(guest, dict):
            return guest.get("name", "")
        if isinstance(guest, str):
            return guest
    return ""


# ---------------------------------------------------------------------------
# Theme Card Builder
# ---------------------------------------------------------------------------


def build_theme_cards(data: JSON) -> str:
    """Build one card per cross-cutting theme."""
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]

    cards: list[str] = []
    for i, theme in enumerate(themes):
        cards.append(_build_single_theme_card(theme, i + 1, len(themes)))

    return "\n\n".join(cards)


def _build_single_theme_card(theme: dict[str, Any], num: int, total: int) -> str:
    """Build a single theme card with progressive disclosure."""
    tid = theme.get("id", f"theme_{num}")
    name = esc(theme.get("name", "Untitled"))
    summary = esc(theme.get("summary", ""))
    narrative = theme.get("narrative", "")
    color_idx = ((num - 1) % 7) + 1

    lines: list[str] = []
    lines.append(f'<article class="card card-theme theme-{color_idx}" id="card-{num}">')

    # Badge
    lines.append(f'  <div class="theme-badge theme-{color_idx}">')
    lines.append(f'    <span class="dot"></span>')
    lines.append(f'    Theme {num} / {total}')
    lines.append(f'  </div>')

    # Claim (big text)
    lines.append(f'  <h2 class="card-claim">{name}</h2>')

    # Summary
    lines.append(f'  <p style="font-size:var(--fs-md);color:var(--text-secondary);margin-bottom:var(--sp-lg)">{summary}</p>')

    # Narrative prose
    if narrative:
        lines.append(f'  <div class="card-narrative">')
        for para in narrative.split("\n"):
            para = para.strip()
            if para:
                lines.append(f'    <p>{esc(para)}</p>')
        lines.append(f'  </div>')

    # Key quote (pull-quote style)
    quotes: list[dict[str, Any]] = theme.get("highlighted_quotes", [])
    if quotes:
        best = quotes[0]
        text = esc(best.get("text", ""))
        ts = best.get("timestamp", "")
        speaker = esc(best.get("speaker", ""))
        ctx = esc(best.get("context_note", ""))
        lines.append(f'  <blockquote class="pull-quote">')
        lines.append(f'    <p>"{text}"</p>')
        cite_parts = []
        if ts:
            cite_parts.append(timestamp_badge(ts))
        if ctx:
            cite_parts.append(ctx)
        if cite_parts:
            lines.append(f'    <cite>{" — ".join(cite_parts)}</cite>')
        lines.append(f'  </blockquote>')

    # "Why this matters" — expandable
    insights: list[dict[str, Any]] = theme.get("highlighted_insights", [])
    if insights:
        lines.append(f'  <div class="expandable">')
        lines.append(f'    <button class="expand-toggle" aria-expanded="false">')
        lines.append(f'      <span class="arrow">▸</span> 为什么这很重要')
        lines.append(f'    </button>')
        lines.append(f'    <div class="expand-content">')
        for ins in insights[:5]:
            claim = esc(ins.get("claim", ""))
            expl = esc(ins.get("explanation", ""))
            lines.append(f'      <div class="insight-item">')
            lines.append(f'        <div class="insight-claim">{claim}</div>')
            if expl:
                lines.append(f'        <div class="insight-expl">{expl}</div>')
            lines.append(f'      </div>')
        lines.append(f'    </div>')
        lines.append(f'  </div>')

    # Related themes link
    related: list[str] = theme.get("related_themes", [])
    if related:
        rnames = esc(", ".join(related[:2]))
        lines.append(f'  <div class="expandable">')
        lines.append(f'    <button class="expand-toggle" aria-expanded="false">')
        lines.append(f'      <span class="arrow">▸</span> 关联主题：{rnames}')
        lines.append(f'    </button>')
        lines.append(f'    <div class="expand-content">')
        lines.append(f'    <p>此主题与以下概念相关联，在知识图谱中可看到连线关系。</p>')
        lines.append(f'    </div>')
        lines.append(f'  </div>')

    # Reading time estimate
    word_count = len(narrative) + sum(len(ins.get("claim", "")) + len(ins.get("explanation", "")) for ins in insights)
    read_time = max(1, round(word_count / 400))
    lines.append(f'  <div style="margin-top:var(--sp-lg);font-family:var(--font-ui);font-size:var(--fs-xs);color:var(--text-muted)">')
    lines.append(f'    ⏱ ~{read_time} min read')
    lines.append(f'  </div>')

    lines.append('</article>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Closing Card Builder
# ---------------------------------------------------------------------------


def build_closing_card(data: JSON) -> str:
    """Build the closing card with 'if you only remember 3 things' and role advice."""
    meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    takeaways = meta.get("key_takeaways", [])

    lines: list[str] = []
    lines.append('<article class="card card-closing" id="card-closing">')

    # Heading
    lines.append('  <h2>如果你只记住三件事</h2>')

    # Top 3 takeaways
    lines.append('  <ol class="remember-list">')
    for i, t in enumerate(takeaways[:3], start=1):
        claim = esc(t.get("claim", ""))
        lines.append(f'    <li class="remember-item">')
        lines.append(f'      <span class="remember-num">{i}</span>')
        lines.append(f'      <span class="remember-text">{claim}</span>')
        lines.append(f'    </li>')
    lines.append('  </ol>')

    # Role-specific advice
    lines.append('  <h3 style="font-size:var(--fs-md);margin-top:var(--sp-xl);margin-bottom:var(--sp-md)">这对你意味着什么？</h3>')
    lines.append('  <div class="role-tabs">')
    lines.append('    <button class="role-tab active" data-role="engineer">🔧 工程师</button>')
    lines.append('    <button class="role-tab" data-role="pm">📋 产品经理</button>')
    lines.append('    <button class="role-tab" data-role="founder">🚀 创业者</button>')
    lines.append('    <button class="role-tab" data-role="investor">💼 投资人</button>')
    lines.append('  </div>')

    # Role content panels
    role_advice = {
        "engineer": "AI coding 已经让开发效率提升 20-50 倍，但这不是终点。核心建议：(1) 不要只做语言模型——末班车已发车，转向多模态生成、机器人或 AI 辅助科学等蓝海方向；(2) 「把简单的事做得比谁都干净」比追求神奇技巧更重要——工程质量是真正的护城河；(3) 培养系统性思维——AI 已进入集体主义时代，个人英雄主义终结。",
        "pm": "姚顺宇的判断可能让你不安：产品经理是 AI 最难替代的工作——因为「没有标准就是没有刻度」。但这也意味着：(1) 定义清楚「要解决什么问题」成为最稀缺的能力；(2) AI 产品交互形态远未定型——chatbot 不是终局，long horizon 任务执行是下一个前沿；(3) 中国 C 端产品模式（先不挣钱再形成闭环）值得深入研究。",
        "founder": "姚顺宇给出了冷酷但清晰的生存框架：(1) AI 应用创业只有两条路：Cursor 式逃逸速度（万分之一生存率）或 Midjourney 式 niche 市场（百分之一）；(2) 「先吃一个小的，但选择有想象空间的小的」；(3) 目前只在模型侧有壁垒——如果做应用层，必须想清楚模型公司追上来怎么办。",
        "investor": "几个值得关注的结构性判断：(1) 语言模型窗口已关闭，多模态生成和机器人是下一波范式突破方向；(2) 中国 AI 人才被严重低估——算力劣势逼出的软蒸馏创新可能是真正的 multi-agent 训练先驱；(3) ByteDance 是被严重低估的公司；(4) 绝大多数硅谷 new AI lab 会死——关注组织 DNA 和技术 leader 质量。",
    }

    for role_key, advice in role_advice.items():
        visible = ' visible' if role_key == "engineer" else ''
        lines.append(f'  <div class="role-content{visible}" data-role="{role_key}">')
        lines.append(f'    <p>{esc(advice)}</p>')
        lines.append(f'  </div>')

    # Links to other formats
    lines.append('  <div class="closing-links">')
    lines.append('    <a href="#" class="btn btn-secondary" data-goto="0">← 回到封面</a>')
    lines.append('  </div>')

    lines.append('</article>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Nav Dots Builder
# ---------------------------------------------------------------------------


def build_nav_dots(data: JSON) -> str:
    """Build the side navigation dots."""
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    total = len(themes) + 2  # hero + themes + closing

    lines: list[str] = []
    for i in range(total):
        active = ' active' if i == 0 else ''
        lines.append(f'<button class="nav-dot{active}" data-index="{i}" aria-label="Card {i+1}"></button>')

    return "\n  ".join(lines)


# ---------------------------------------------------------------------------
# Title Helpers
# ---------------------------------------------------------------------------


def build_title(data: JSON, knowledge_data: JSON | None = None) -> str:
    """Build full page title."""
    if knowledge_data:
        meta: dict[str, Any] = knowledge_data.get("metadata", {})  # type: ignore[assignment]
        if meta.get("title"):
            return esc(meta["title"])
    vc_meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    return esc(vc_meta.get("title", "Interview — Learning Cards"))


def build_title_short(data: JSON) -> str:
    """Build short title for top bar."""
    guest = _get_guest_name(data)
    if guest:
        # Take last name or first few chars
        parts = guest.split()
        short = parts[-1] if parts else guest[:6]
        return esc(f"{short} · Learning Cards")
    return "Learning Cards"


# ---------------------------------------------------------------------------
# Core Rendering
# ---------------------------------------------------------------------------


def read_template_files(template_dir: str) -> tuple[str, str, str]:
    """Read the three template files."""
    base = Path(template_dir)
    html_path = base / "index.html"
    css_path = base / "style.css"
    js_path = base / "script.js"

    missing: list[str] = []
    for p in (html_path, css_path, js_path):
        if not p.is_file():
            missing.append(str(p))
    if missing:
        raise FileNotFoundError(f"Template files not found: {', '.join(missing)}")

    return (
        html_path.read_text(encoding="utf-8"),
        css_path.read_text(encoding="utf-8"),
        js_path.read_text(encoding="utf-8"),
    )


def render_cards(
    data: JSON,
    html_template: str,
    css_content: str,
    js_content: str,
    knowledge_data: JSON | None = None,
) -> str:
    """Produce the final self-contained learning cards HTML."""
    # Build content blocks
    title = build_title(data, knowledge_data)
    title_short = build_title_short(data)
    hero_html = build_hero_card(data)
    theme_html = build_theme_cards(data)
    closing_html = build_closing_card(data)
    nav_dots_html = build_nav_dots(data)

    # Inline CSS and JS
    result = html_template.replace(
        '<link rel="stylesheet" href="style.css">',
        f"<style>\n{css_content}\n</style>",
    )
    result = result.replace(
        '<script src="script.js"></script>',
        f"<script>\n{js_content}\n</script>",
    )

    # Substitute template variables
    replacements: dict[str, str] = {
        "{{TITLE}}": title,
        "{{TITLE_SHORT}}": title_short,
        "{{HERO_CARD_HTML}}": hero_html,
        "{{THEME_CARDS_HTML}}": theme_html,
        "{{CLOSING_CARD_HTML}}": closing_html,
        "{{NAV_DOTS_HTML}}": nav_dots_html,
    }

    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)

    return result


def load_json(filepath: str) -> JSON:
    """Load and parse a JSON file."""
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"Invalid JSON in {filepath}: {exc.msg}", exc.doc, exc.pos
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object at root of {filepath}, got {type(data).__name__}"
        )
    return data


def write_output(html: str, output_path: str) -> None:
    """Write the rendered HTML to a file."""
    try:
        out = Path(output_path)
        out.write_text(html, encoding="utf-8")
        print(f"Cards written to: {out.resolve()}", file=sys.stderr)
    except OSError as exc:
        print(f"Error writing to {output_path}: {exc}", file=sys.stderr)
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate interactive learning cards HTML from visual_content.json.",
    )
    parser.add_argument(
        "visual_content_json",
        metavar="VISUAL_CONTENT_JSON",
        help="Path to visual_content.json input file.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        default="cards.html",
        help="Path for output HTML file. Default: cards.html",
    )
    parser.add_argument(
        "--template-dir",
        metavar="DIR",
        default=None,
        help="Path to cards-template directory. Default: ../assets/cards-template/",
    )
    parser.add_argument(
        "--knowledge", "-k",
        metavar="PATH",
        default=None,
        help="Optional path to knowledge.json for metadata.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point."""
    parser = build_argparser()
    args = parser.parse_args(argv)

    # Resolve template directory
    if args.template_dir:
        template_dir = args.template_dir
    else:
        script_dir = Path(__file__).resolve().parent
        template_dir = str(script_dir.parent / "assets" / "cards-template")

    # Load visual_content.json
    try:
        data = load_json(args.visual_content_json)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Load optional knowledge.json
    knowledge_data = None
    if args.knowledge:
        try:
            knowledge_data = load_json(args.knowledge)
        except Exception as exc:
            print(f"Warning: Could not load knowledge.json: {exc}", file=sys.stderr)

    # Read template files
    try:
        html_template, css_content, js_content = read_template_files(template_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Render
    try:
        html = render_cards(data, html_template, css_content, js_content, knowledge_data)
    except Exception as exc:
        print(f"Error rendering cards: {exc}", file=sys.stderr)
        sys.exit(2)

    # Write output
    try:
        write_output(html, args.output)
    except OSError:
        sys.exit(1)


if __name__ == "__main__":
    main()
