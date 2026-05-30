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
# I18n dictionary
# ---------------------------------------------------------------------------

UI_TEXT: dict[str, dict[str, str]] = {
    "zh": {
        "subtitle": "一场{dur}的深度对话，浓缩为{theme_n}个核心洞察",
        "start_learning": "开始学习 →",
        "jump_to_summary": "跳到总结",
        "why_matters": "为什么这很重要",
        "related_themes_label": "关联主题",
        "related_themes_hint": "此主题与以下概念相关联，在知识图谱中可看到连线关系。",
        "closing_heading": "如果你只记住三件事",
        "role_question": "这对你意味着什么？",
        "role_fallback": "阅读完整报告以获取详细分析和建议。",
    },
    "en": {
        "subtitle": "{theme_n} core insights distilled from a {dur} deep conversation",
        "start_learning": "Start Learning →",
        "jump_to_summary": "Jump to Summary",
        "why_matters": "Why This Matters",
        "related_themes_label": "Related Themes",
        "related_themes_hint": "This theme connects to the following concepts, visible as linked nodes in the knowledge graph.",
        "closing_heading": "If You Only Remember Three Things",
        "role_question": "What Does This Mean For You?",
        "role_fallback": "Read the full report for detailed analysis and recommendations.",
    },
}


# ---------------------------------------------------------------------------
# Color palette (12 colors for cycling)
# ---------------------------------------------------------------------------

ALL_COLORS: list[str] = [
    "#6C5CE7",  # Purple
    "#00B894",  # Green
    "#E17055",  # Coral/Orange
    "#0984E3",  # Blue
    "#FDCB6E",  # Yellow
    "#E84393",  # Pink
    "#00CEC9",  # Teal
    "#D63031",  # Red
    "#A29BFE",  # Lavender
    "#55EFC4",  # Mint
    "#74B9FF",  # Sky blue
    "#FFEAA7",  # Light yellow
]


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


def build_hero_card(data: JSON, lang: str = "zh", knowledge_data: JSON | None = None) -> str:
    """Build the hero/cover card with compact overview and theme index grid."""
    meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    tx: dict[str, str] = UI_TEXT.get(lang, UI_TEXT["zh"])
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]

    thesis = esc(meta.get("core_thesis", ""))
    stats = meta.get("stats", {})
    dur = esc(str(stats.get("duration_formatted", "")))
    theme_n = len(themes)
    insight_count = stats.get("insight_count", theme_n)

    # Guest info — prefer knowledge_data metadata, fall back to visual_content meta
    guest_name = _get_guest_name(knowledge_data) if knowledge_data else _get_guest_name(data)
    if not guest_name:
        guest_name = _get_guest_name(data)
    affiliation = _get_guest_affiliation(knowledge_data) if knowledge_data else _get_guest_affiliation(data)
    if not affiliation:
        affiliation = _get_guest_affiliation(data)
    guest_display = guest_name
    if affiliation:
        guest_display = f"{guest_name}, {affiliation}"

    lines: list[str] = []
    lines.append('<article class="card card-hero" id="card-0">')

    # Guest info row
    lines.append(f'  <div class="hero-guest">🎙 {esc(guest_display)}</div>')

    # Stats row
    lines.append(f'  <div class="hero-stats">⏱ {dur} · {insight_count} core insights</div>')

    # Core thesis as a styled pull-quote
    lines.append(f'  <blockquote class="hero-thesis">{thesis}</blockquote>')

    # Theme index label
    lines.append('  <div class="theme-index-label">📋 Content</div>')

    # Theme index grid
    lines.append('  <div class="theme-index">')
    for i, theme in enumerate(themes):
        name = esc(theme.get("name", f"Theme {i+1}"))
        summary = esc(theme.get("summary", ""))
        color = theme.get("color") or ALL_COLORS[i % len(ALL_COLORS)]
        # Truncate summary to 60 chars
        if len(summary) > 60:
            summary = summary[:57] + "..."
        lines.append(f'    <button class="theme-index-tile" data-theme-index="{i+1}" style="border-left: 3px solid {color}">')
        lines.append(f'      <span class="tile-name">{name}</span>')
        lines.append(f'      <span class="tile-summary">{summary}</span>')
        lines.append(f'    </button>')
    lines.append('  </div>')

    # Start button
    lines.append(f'  <button class="btn btn-primary hero-start">{tx["start_learning"]}</button>')

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


def _get_guest_affiliation(data: JSON) -> str:
    """Extract guest affiliation from metadata."""
    meta = data.get("meta", data.get("metadata", {}))
    if isinstance(meta, dict):
        guest = meta.get("guest", "")
        if isinstance(guest, dict):
            return guest.get("affiliation", "")
    return ""


# ---------------------------------------------------------------------------
# Theme Card Builder
# ---------------------------------------------------------------------------


def build_theme_cards(data: JSON, lang: str = "zh") -> str:
    """Build one card per cross-cutting theme."""
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]

    cards: list[str] = []
    for i, theme in enumerate(themes):
        # Attach full themes list so each card can look up the next theme name
        theme["_all_themes"] = themes
        cards.append(_build_single_theme_card(theme, i + 1, len(themes), lang))

    return "\n\n".join(cards)


def _build_single_theme_card(theme: dict[str, Any], num: int, total: int, lang: str = "zh") -> str:
    """Build a single theme card with progressive disclosure."""
    tx: dict[str, str] = UI_TEXT.get(lang, UI_TEXT["zh"])
    tid = theme.get("id", f"theme_{num}")
    name = esc(theme.get("name", "Untitled"))
    summary = esc(theme.get("summary", ""))
    narrative = theme.get("narrative", "")

    # Use theme's own color if specified, otherwise cycle through ALL_COLORS
    color = theme.get("color") or ALL_COLORS[(num - 1) % len(ALL_COLORS)]

    lines: list[str] = []
    lines.append(f'<article class="card card-theme" id="card-{num}" style="--theme-color: {color}">')

    # Badge
    lines.append(f'  <div class="theme-badge">')
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
        lines.append(f'      <span class="arrow">▸</span> {tx["why_matters"]}')
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
        lines.append(f'      <span class="arrow">▸</span> {tx["related_themes_label"]}：{rnames}')
        lines.append(f'    </button>')
        lines.append(f'    <div class="expand-content">')
        lines.append(f'    <p>{tx["related_themes_hint"]}</p>')
        lines.append(f'    </div>')
        lines.append(f'  </div>')

    # Reading time estimate
    word_count = len(narrative) + sum(len(ins.get("claim", "")) + len(ins.get("explanation", "")) for ins in insights)
    read_time = max(1, round(word_count / 400))
    lines.append(f'  <div style="margin-top:var(--sp-lg);font-family:var(--font-ui);font-size:var(--fs-xs);color:var(--text-muted)">')
    lines.append(f'    ⏱ ~{read_time} min read')
    lines.append(f'  </div>')

    # Next-theme navigation (skip for the last card)
    if num < total:
        themes_all: list[dict[str, Any]] = theme.get("_all_themes", [])
        next_name = ""
        if themes_all and num < len(themes_all):
            next_name = themes_all[num].get("name", "")
        if not next_name:
            next_name = f"Theme {num+1}"
        lines.append(f'  <div class="next-theme">')
        lines.append(f'    <span class="next-theme-label">Next</span>')
        lines.append(f'    <button class="next-theme-btn" data-next-index="{num+1}">{esc(next_name)} →</button>')
        lines.append(f'  </div>')

    lines.append('</article>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Closing Card Builder
# ---------------------------------------------------------------------------


def build_closing_card(data: JSON, lang: str = "zh", knowledge_data: JSON | None = None) -> str:
    """Build the closing card with 'if you only remember 3 things', role advice, and external links."""
    meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    tx: dict[str, str] = UI_TEXT.get(lang, UI_TEXT["zh"])
    takeaways = meta.get("key_takeaways", [])

    lines: list[str] = []
    lines.append('<article class="card card-closing" id="card-closing">')

    # Heading
    lines.append(f'  <h2>{tx["closing_heading"]}</h2>')

    # Top 3 takeaways
    lines.append('  <ol class="remember-list">')
    for i, t in enumerate(takeaways[:3], start=1):
        claim = esc(t.get("claim", ""))
        lines.append(f'    <li class="remember-item">')
        lines.append(f'      <span class="remember-num">{i}</span>')
        lines.append(f'      <span class="remember-text">{claim}</span>')
        lines.append(f'    </li>')
    lines.append('  </ol>')

    # Role-specific advice — read from visual_content meta if present, otherwise fall back
    role_advice: dict[str, Any] = meta.get("role_advice", {})  # type: ignore[assignment]
    if isinstance(role_advice, dict) and role_advice:
        lines.append(f'  <h3 style="font-size:var(--fs-md);margin-top:var(--sp-xl);margin-bottom:var(--sp-md)">{tx["role_question"]}</h3>')
        lines.append('  <div class="role-tabs">')
        first = True
        for role_key in role_advice:
            active_class = ' active' if first else ''
            lines.append(f'    <button class="role-tab{active_class}" data-role="{esc(role_key)}">{esc(role_key)}</button>')
            first = False
        lines.append('  </div>')

        first = True
        for role_key, advice in role_advice.items():
            visible = ' visible' if first else ''
            lines.append(f'  <div class="role-content{visible}" data-role="{esc(role_key)}">')
            lines.append(f'    <p>{esc(str(advice))}</p>')
            lines.append(f'  </div>')
            first = False
    else:
        lines.append(f'  <p style="font-size:var(--fs-md);margin-top:var(--sp-xl);color:var(--text-secondary)">{tx["role_fallback"]}</p>')

    # External links to other output formats
    filenames = _build_output_filenames(data, knowledge_data)
    lines.append('  <div class="closing-links">')
    lines.append('    <span class="closing-links-label">Continue Exploring</span>')
    lines.append(f'    <a href="{esc(filenames["report"])}" class="btn btn-secondary">Full Report →</a>')
    lines.append(f'    <a href="{esc(filenames["map"])}" class="btn btn-secondary">Knowledge Map →</a>')
    lines.append(f'    <a href="{esc(filenames["tldr"])}" class="btn btn-secondary">TL;DR →</a>')
    lines.append('  </div>')

    lines.append('</article>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output Filename Helper
# ---------------------------------------------------------------------------


def _build_output_filenames(data: JSON, knowledge_data: JSON | None = None) -> dict[str, str]:
    """Construct relative filenames for report, map, and tldr output files.

    Naming convention:
        tldr-[guest-slug]-[YYYYMMDD].md
        report-[guest-slug]-[YYYYMMDD].md
        map-[guest-slug]-[YYYYMMDD].html

    Guest slug is derived from the guest name (last word of the Latin/pinyin name).
    Date is extracted from visual_content.json meta.date or knowledge.json metadata.date,
    falling back to today's date.
    """
    # --- guest slug (prefer knowledge_data, fall back to visual_content) ---
    guest_name = _get_guest_name(knowledge_data) if knowledge_data else ""
    if not guest_name:
        guest_name = _get_guest_name(data)
    slug = _guest_slug(guest_name)

    # --- date ---
    date_str = _extract_date(data, knowledge_data)

    return {
        "tldr": f"tldr-{slug}-{date_str}.md",
        "report": f"report-{slug}-{date_str}.md",
        "map": f"map-{slug}-{date_str}.html",
    }


def _guest_slug(guest_name: str) -> str:
    """Derive a filename-safe slug from the guest name.

    Takes the last word of the name (typically the surname/family name in
    Latin script), strips non-alphanumeric characters, and lowercases.
    Falls back to 'guest' when the name is empty or purely non-Latin.
    """
    if not guest_name:
        return "guest"
    # Split on whitespace, take the last word
    parts = guest_name.strip().split()
    last = parts[-1] if parts else guest_name
    # Remove parentheses, brackets, and other non-alphanumeric chars
    cleaned = "".join(ch for ch in last if ch.isalnum())
    if not cleaned:
        return "guest"
    return cleaned.lower()


def _extract_date(data: JSON, knowledge_data: JSON | None = None) -> str:
    """Extract YYYYMMDD date from available metadata sources.

    Priority order:
    1. visual_content.json meta.date
    2. knowledge.json metadata.date
    3. Today's date (fallback)
    """
    from datetime import date as _date

    # Try visual_content meta
    meta = data.get("meta", {})
    if isinstance(meta, dict):
        d = meta.get("date", "")
        if d and isinstance(d, str) and len(d) >= 8:
            return _normalize_date(d)

    # Try knowledge metadata
    if knowledge_data:
        km = knowledge_data.get("metadata", {})
        if isinstance(km, dict):
            d = km.get("date", "")
            if d and isinstance(d, str) and len(d) >= 8:
                return _normalize_date(d)

    # Fall back to today
    return _date.today().strftime("%Y%m%d")


def _normalize_date(raw: str) -> str:
    """Normalize a date string to YYYYMMDD format."""
    # Strip non-digit characters and take first 8 digits
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) >= 8:
        return digits[:8]
    return digits


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
    lang: str = "zh",
) -> str:
    """Produce the final self-contained learning cards HTML."""
    # Build content blocks
    title = build_title(data, knowledge_data)
    title_short = build_title_short(data)
    hero_html = build_hero_card(data, lang, knowledge_data)
    theme_html = build_theme_cards(data, lang)
    closing_html = build_closing_card(data, lang, knowledge_data)
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
    parser.add_argument(
        "--lang", "-l",
        metavar="LANG",
        default="zh",
        choices=["zh", "en"],
        help="Language for UI strings. Default: zh. Supported: zh, en.",
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
        html = render_cards(data, html_template, css_content, js_content, knowledge_data, args.lang)
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
