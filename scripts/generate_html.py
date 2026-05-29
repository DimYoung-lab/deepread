#!/usr/bin/env python3
"""Render a self-contained interactive HTML interview report from knowledge.json.

Reads a knowledge.json file (produced by the interview analysis pipeline),
combines it with the report-template assets (index.html, style.css, script.js),
and writes a single standalone HTML file with all CSS/JS inlined.

Usage:
    python generate_html.py knowledge.json
    python generate_html.py knowledge.json --output report.html
    python generate_html.py knowledge.json -o report.html --template-dir assets/report-template/

Template variables replaced in index.html:
    {{TITLE}}           – interview title
    {{METADATA_HTML}}   – header metadata (guest, date, duration, stats)
    {{SIDEBAR_HTML}}    – sidebar navigation links from segments
    {{CONTENT_HTML}}    – main topic-by-topic deep-dive sections
    {{QUOTES_HTML}}     – supplemental: all golden quotes by segment
    {{PREDICTIONS_HTML}}– supplemental: predictions summary table
    {{THEMES_HTML}}     – supplemental: cross-cutting themes
"""

from __future__ import annotations

import argparse
import html as _html
import json
import os
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIDENCE_LABELS: dict[str, str] = {
    "high": "High confidence",
    "medium": "Medium confidence",
    "low": "Low confidence",
}

CONFIDENCE_CSS: dict[str, str] = {
    "high": "conf-high",
    "medium": "conf-med",
    "low": "conf-low",
}

DATA_TYPE_ICONS: dict[str, str] = {
    "statistic": "#",
    "entity": "E",
    "benchmark": "B",
    "paper": "P",
    "event": "!",
    "forecast": "F",
}

DATA_TYPE_CSS: dict[str, str] = {
    "statistic": "type-green",
    "entity": "type-blue",
    "benchmark": "type-amber",
    "paper": "type-purple",
    "event": "type-red",
    "forecast": "type-blue",
}

SECTION_ID_PREFIX = "seg-"

# Supplemental CSS for generated content blocks not styled by the base template.
# Injected immediately after the template CSS in the final HTML.
_SUPPLEMENTAL_CSS = r"""
/* ---- Generated Content Blocks ---- */

/* Segment header */
.segment-header {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: var(--sp-sm); margin-bottom: var(--sp-md);
}
.segment-time-range {
  font-family: var(--font-mono); font-size: var(--fs-sm);
  color: var(--text-muted); white-space: nowrap;
}
.segment-summary {
  font-size: var(--fs-md); line-height: var(--lh-body);
  color: var(--text-secondary); margin-bottom: var(--sp-lg);
  max-width: var(--content-w);
}

/* Key topic tags */
.key-topics {
  display: flex; flex-wrap: wrap; gap: var(--sp-sm);
  margin-bottom: var(--sp-lg);
}
.topic-tag {
  display: inline-block; padding: 2px var(--sp-md);
  font-size: var(--fs-sm); border-radius: var(--r-pill);
  background: var(--accent-soft); color: var(--accent);
  border: 1px solid var(--border); font-family: var(--font-mono);
}

/* Insight cards */
.insights-block, .quotes-block, .datapoints-block,
.contradictions-block, .predictions-block {
  margin-bottom: var(--sp-xl);
}
.insight-card {
  margin: var(--sp-md) 0; padding: var(--sp-md) var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface); transition: box-shadow var(--t-fast);
}
.insight-card:hover { box-shadow: var(--shadow-sm); }
.insight-header {
  display: flex; align-items: center; gap: var(--sp-sm);
  margin-bottom: var(--sp-sm);
}
.insight-type-badge {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  padding: 1px var(--sp-sm); border-radius: var(--r-pill);
  background: var(--accent-soft); color: var(--accent);
  text-transform: uppercase; letter-spacing: .04em;
}
.insight-claim {
  font-weight: 600; font-size: var(--fs-base);
  line-height: var(--lh-compact); margin-bottom: var(--sp-xs);
}
.insight-explanation {
  font-size: var(--fs-sm); color: var(--text-secondary);
  line-height: var(--lh-compact);
}

/* Contradiction callout */
.contradiction-callout {
  margin: var(--sp-md) 0; padding: var(--sp-md) var(--sp-lg);
  border: 1px solid var(--border); border-left: 4px solid #c45a4a;
  border-radius: 0 var(--r-md) var(--r-md) 0;
  background: var(--bg-alt);
}
.contradiction-label {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: #c45a4a; text-transform: uppercase;
  letter-spacing: .05em; margin-bottom: var(--sp-xs);
}
.contradiction-context {
  font-size: var(--fs-sm); color: var(--text-muted);
  margin-top: var(--sp-xs);
}

/* Predictions inside segments */
.prediction-item .prediction-confidence.conf-high { color: #4a9e6b; }
.prediction-item .prediction-confidence.conf-med  { color: #c4943a; }
.prediction-item .prediction-confidence.conf-low  { color: #c45a4a; }
.prediction-statement { font-weight: 600; margin-bottom: var(--sp-xs); }
.prediction-horizon, .prediction-conditions {
  font-size: var(--fs-sm); color: var(--text-secondary);
}

/* Data timestamp */
.data-timestamp { margin-top: var(--sp-xs); }

/* Predictions summary table */
.predictions-table {
  width: 100%; border-collapse: collapse;
  font-size: var(--fs-sm); line-height: var(--lh-compact);
  margin: var(--sp-lg) 0;
}
.predictions-table th {
  text-align: left; padding: var(--sp-sm) var(--sp-md);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: .05em; border-bottom: 2px solid var(--border);
  background: var(--bg-alt);
}
.predictions-table td {
  padding: var(--sp-sm) var(--sp-md);
  border-bottom: 1px solid var(--border-light);
  vertical-align: top;
}
.predictions-table tbody tr:hover { background: var(--accent-soft); }
.pred-num {
  width: 2rem; text-align: right;
  font-family: var(--font-mono); color: var(--text-muted);
}
.pred-badge {
  display: inline-block; padding: 1px var(--sp-sm);
  font-size: var(--fs-xs); font-family: var(--font-mono);
  border-radius: var(--r-pill); white-space: nowrap;
}
.pred-badge.conf-high { background: rgba(74,158,107,0.15); color: #4a9e6b; }
.pred-badge.conf-med  { background: rgba(196,148,58,0.15); color: #c4943a; }
.pred-badge.conf-low  { background: rgba(196,90,74,0.15); color: #c45a4a; }
.pred-conditions { font-size: var(--fs-xs); color: var(--text-muted); max-width: 18rem; }

/* Theme blocks */
.theme-block {
  margin-bottom: var(--sp-xl); padding: var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface);
}
.theme-refs { margin-top: var(--sp-md); display: flex; flex-wrap: wrap; gap: var(--sp-sm); align-items: center; }
.theme-ref-label { font-size: var(--fs-sm); color: var(--text-muted); }

/* Quote group in supplemental */
.quote-group { margin-bottom: var(--sp-xl); }
.quote-group h3 {
  font-family: var(--font-heading); font-size: var(--fs-md);
  margin-bottom: var(--sp-md);
}

/* Empty state */
.empty-message {
  color: var(--text-muted); font-style: italic;
  text-align: center; padding: var(--sp-3xl) var(--sp-xl);
}
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_duration(seconds: int) -> str:
    """Format total seconds to a human-readable duration string.

    >>> format_duration(3661)
    '1h 1m'
    >>> format_duration(65)
    '1m 5s'
    >>> format_duration(42)
    '42s'
    """
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts: list[str] = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return " ".join(parts)


def timestamp_badge(ts: str) -> str:
    """Render a clickable timestamp span.

    Args:
        ts: Timestamp string in HH:MM:SS or MM:SS format.

    Returns:
        HTML span element with data-time attribute.
    """
    escaped = _html.escape(ts)
    return f'<span class="timestamp-badge" data-time="{escaped}">{escaped}</span>'


def esc(text: str, quote: bool = True) -> str:
    """Short alias for html.escape.

    Args:
        text: The string to escape.
        quote: If True (default), also escape double-quote characters.
    """
    return _html.escape(text, quote=quote)


def make_section_id(segment_id: str) -> str:
    """Generate a stable HTML anchor id from a segment identifier."""
    return SECTION_ID_PREFIX + _html.escape(segment_id, quote=True)


# ---------------------------------------------------------------------------
# Template variable builders
# ---------------------------------------------------------------------------


def build_title(data: JSON) -> str:
    """Extract and escape the report title from knowledge.json metadata."""
    meta: dict[str, Any] = data.get("metadata", {})  # type: ignore[assignment]
    title: str = meta.get("title", "Interview Report")
    return esc(title)


def build_metadata_html(data: JSON) -> str:
    """Build the metadata line shown under the report title.

    Produces something like:
        Guest Name   ·   Show Name   ·   2024-03-15   ·   2h 15m   ·   8 segments
    """
    meta: dict[str, Any] = data.get("metadata", {})  # type: ignore[assignment]
    segments: list[Any] = data.get("segments", [])  # type: ignore[assignment]

    pieces: list[str] = []

    guest = meta.get("guest", {})
    if isinstance(guest, dict) and guest.get("name"):
        pieces.append(f'<span class="meta-guest">{esc(guest["name"])}</span>')
        if guest.get("affiliation"):
            pieces[-1] = f'<span class="meta-guest">{esc(guest["name"])}, {esc(guest["affiliation"])}</span>'

    interviewer = meta.get("interviewer", {})
    if isinstance(interviewer, dict) and interviewer.get("name"):
        pieces.append(f'<span class="meta-host">Host: {esc(interviewer["name"])}</span>')

    if meta.get("date"):
        pieces.append(f'<span class="meta-date">{esc(meta["date"])}</span>')

    duration = meta.get("duration_seconds") or meta.get("total_duration_seconds") or 0
    if duration:
        pieces.append(f'<span class="meta-duration">{esc(format_duration(int(duration)))}</span>')

    if segments:
        pieces.append(f'<span class="meta-stat">{len(segments)} segments</span>')

    # Count total quotes and predictions across all segments
    total_quotes = sum(len(s.get("golden_quotes", [])) for s in segments)
    total_predictions = sum(len(s.get("predictions", [])) for s in segments)

    if total_quotes:
        pieces.append(f'<span class="meta-stat">{total_quotes} quotes</span>')
    if total_predictions:
        pieces.append(f'<span class="meta-stat">{total_predictions} predictions</span>')

    return "\n        ".join(pieces)


def build_sidebar_html(data: JSON) -> str:
    """Build the sidebar navigation list from segments."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]

    if not segments:
        return '<nav><ul><li><em>No segments found.</em></li></ul></nav>'

    items: list[str] = ["<nav><ul>"]
    for seg in segments:
        sid = seg.get("id", "")
        title = esc(seg.get("title", "Untitled"))
        tr = seg.get("time_range", {})
        start = tr.get("start", "") if isinstance(tr, dict) else ""
        section_id = make_section_id(sid)
        label = f"{title}"
        if start:
            label += f" <small>{esc(start)}</small>"
        items.append(
            f'  <li><a href="#{section_id}">{label}</a></li>'
        )
    items.append("</ul></nav>")
    return "\n".join(items)


def build_content_html(data: JSON) -> str:
    """Build the main content area with all segment sections."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]

    if not segments:
        return '<p class="empty-message">No segments to display.</p>'

    sections: list[str] = []
    for seg in segments:
        sections.append(_render_segment(seg))

    return "\n\n".join(sections)


def _render_segment(seg: dict[str, Any]) -> str:
    """Render a single segment as a collapsible HTML details element."""
    sid = seg.get("id", "")
    title = esc(seg.get("title", "Untitled"))
    section_id = make_section_id(sid)

    tr = seg.get("time_range", {})
    time_start = tr.get("start", "") if isinstance(tr, dict) else ""
    time_end = tr.get("end", "") if isinstance(tr, dict) else ""

    lines: list[str] = []
    # Use <details open> for native collapsible behavior — sidebar links and JS expand/collapse target these
    lines.append(f'<details open id="{section_id}" class="segment-details" data-segment-id="{esc(sid, quote=True)}" aria-labelledby="heading-{section_id}">')

    # Title + time range header as clickable <summary>
    time_range_html = f'{esc(time_start)} – {esc(time_end)}' if time_start and time_end else ""
    lines.append(f'  <summary class="segment-header">')
    lines.append(f'    <h2 id="heading-{section_id}">{title}</h2>')
    if time_range_html:
        lines.append(f'    <span class="segment-time-range">{time_range_html}</span>')
    lines.append(f'  </summary>')

    # Summary
    summary = seg.get("summary", "")
    if summary:
        lines.append(f'  <p class="segment-summary">{esc(summary)}</p>')

    # Key topics as tag badges
    key_topics: list[str] = seg.get("key_topics", [])
    if key_topics:
        tags = "\n".join(
            f'    <span class="topic-tag">{esc(t)}</span>' for t in key_topics
        )
        lines.append(f'  <div class="key-topics">')
        lines.append(tags)
        lines.append(f'  </div>')

    # Insights as structured cards
    insights: list[dict[str, Any]] = seg.get("insights", [])
    if insights:
        lines.append(f'  <div class="insights-block">')
        lines.append(f'    <h3>Key Insights</h3>')
        for ins in insights:
            lines.append(_render_insight_card(ins))
        lines.append(f'  </div>')

    # Golden quotes as blockquote elements
    quotes: list[dict[str, Any]] = seg.get("golden_quotes", [])
    if quotes:
        lines.append(f'  <div class="quotes-block">')
        lines.append(f'    <h3>Golden Quotes</h3>')
        for q in quotes:
            lines.append(_render_quote_block(q))
        lines.append(f'  </div>')

    # Data points as info cards
    data_points: list[dict[str, Any]] = seg.get("data_points", [])
    if data_points:
        lines.append(f'  <div class="datapoints-block">')
        lines.append(f'    <h3>Data Points</h3>')
        for dp in data_points:
            lines.append(_render_data_point(dp))
        lines.append(f'  </div>')

    # Contradictions as callout boxes
    contradictions: list[dict[str, Any]] = seg.get("contradictions", [])
    if contradictions:
        lines.append(f'  <div class="contradictions-block">')
        lines.append(f'    <h3>Contradictions &amp; Open Questions</h3>')
        for ct in contradictions:
            lines.append(_render_contradiction(ct))
        lines.append(f'  </div>')

    # Predictions in this segment
    predictions: list[dict[str, Any]] = seg.get("predictions", [])
    if predictions:
        lines.append(f'  <div class="predictions-block">')
        lines.append(f'    <h3>Predictions</h3>')
        for pred in predictions:
            lines.append(_render_prediction_card(pred))
        lines.append(f'  </div>')

    lines.append("</details>")
    return "\n".join(lines)


def _render_insight_card(insight: dict[str, Any]) -> str:
    """Render a single insight as a structured card."""
    claim = esc(insight.get("claim", ""))
    explanation = esc(insight.get("explanation", ""))
    ins_type = esc(insight.get("type", ""))
    ts = insight.get("timestamp", "")

    lines: list[str] = []
    lines.append(f'    <div class="insight-card">')
    lines.append(f'      <div class="insight-header">')

    if ins_type:
        lines.append(f'        <span class="insight-type-badge">{ins_type}</span>')
    if ts:
        lines.append(f'        {timestamp_badge(ts)}')

    lines.append(f'      </div>')
    lines.append(f'      <div class="insight-claim">{claim}</div>')
    if explanation:
        lines.append(f'      <div class="insight-explanation">{explanation}</div>')
    lines.append(f'    </div>')
    return "\n".join(lines)


def _render_quote_block(quote: dict[str, Any]) -> str:
    """Render a single golden quote as a blockquote element."""
    text = esc(quote.get("text", ""))
    ts = quote.get("timestamp", "")
    context = esc(quote.get("context", ""))

    lines: list[str] = []
    lines.append(f'    <blockquote class="insight-quote" data-timestamp="{esc(ts, quote=True)}">')
    lines.append(f'      <p>{text}</p>')
    if ts or context:
        cite_parts: list[str] = []
        if ts:
            cite_parts.append(timestamp_badge(ts))
        if context:
            cite_parts.append(esc(context))
        lines.append(f'      <cite>{" — ".join(cite_parts)}</cite>')
    lines.append(f'    </blockquote>')
    return "\n".join(lines)


def _render_data_point(dp: dict[str, Any]) -> str:
    """Render a single data point as a compact info card."""
    label = esc(dp.get("label", ""))
    value = esc(dp.get("value", ""))
    note = esc(dp.get("note", ""))
    dp_type = dp.get("type", "statistic")
    ts = dp.get("timestamp", "")
    css_class = DATA_TYPE_CSS.get(dp_type, "type-green")
    icon = DATA_TYPE_ICONS.get(dp_type, "?")

    lines: list[str] = []
    lines.append(f'    <div class="data-point {esc(css_class, quote=True)}">')
    lines.append(f'      <div class="data-label">{icon} {esc(dp_type)}</div>')
    lines.append(f'      <div class="data-value">{label}: {value}</div>')
    if note:
        lines.append(f'      <div class="data-note">{note}</div>')
    if ts:
        lines.append(f'      <div class="data-timestamp">{timestamp_badge(ts)}</div>')
    lines.append(f'    </div>')
    return "\n".join(lines)


def _render_contradiction(ct: dict[str, Any]) -> str:
    """Render a contradiction / open question as a callout box."""
    statement = esc(ct.get("statement", ""))
    context = esc(ct.get("context", ""))
    ts = ct.get("timestamp", "")

    lines: list[str] = []
    lines.append(f'    <div class="contradiction-callout">')
    lines.append(f'      <div class="contradiction-label">Tension / Open Question</div>')
    lines.append(f'      <p>{statement}</p>')
    if context:
        lines.append(f'      <p class="contradiction-context">{context}</p>')
    if ts:
        lines.append(f'      {timestamp_badge(ts)}')
    lines.append(f'    </div>')
    return "\n".join(lines)


def _render_prediction_card(pred: dict[str, Any]) -> str:
    """Render a single prediction as a compact card with confidence indicator."""
    statement = esc(pred.get("statement", ""))
    time_horizon = esc(pred.get("time_horizon", ""))
    confidence = pred.get("confidence", "medium")
    conditions = esc(pred.get("conditions", ""))
    conf_label = CONFIDENCE_LABELS.get(confidence, confidence)
    conf_css = CONFIDENCE_CSS.get(confidence, "conf-med")

    lines: list[str] = []
    lines.append(f'    <div class="prediction-item">')
    lines.append(f'      <div class="prediction-confidence {esc(conf_css, quote=True)}">{esc(conf_label)}</div>')
    lines.append(f'      <div class="prediction-statement">{statement}</div>')
    if time_horizon:
        lines.append(f'      <div class="prediction-horizon">Time horizon: {time_horizon}</div>')
    if conditions:
        lines.append(f'      <div class="prediction-conditions">Conditions: {conditions}</div>')
    lines.append(f'    </div>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Supplemental section builders
# ---------------------------------------------------------------------------


def build_quotes_html(data: JSON) -> str:
    """Build the collected golden-quotes section grouped by segment."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]

    collected: list[tuple[str, str, list[dict[str, Any]]]] = []
    for seg in segments:
        quotes = seg.get("golden_quotes", [])
        if quotes:
            collected.append((seg.get("title", "Unknown"), esc(seg.get("id", "")), quotes))

    if not collected:
        return ""

    lines: list[str] = ['<section class="supplemental-section quotes-collection" aria-labelledby="quotes-heading">']
    lines.append('  <h2 id="quotes-heading">Complete Quote Collection</h2>')

    for seg_title, seg_id, quotes in collected:
        escaped_title = esc(seg_title)
        lines.append(f'  <div class="quote-group">')
        lines.append(f'    <h3>{escaped_title}</h3>')
        for i, q in enumerate(quotes, start=1):
            text = esc(q.get("text", ""))
            ts = q.get("timestamp", "")
            context = esc(q.get("context", ""))
            lines.append(f'    <blockquote class="insight-quote" data-timestamp="{esc(ts, quote=True)}">')
            lines.append(f'      <p>{text}</p>')
            cite = ""
            if ts:
                cite += timestamp_badge(ts)
            if context:
                if cite:
                    cite += " — "
                cite += context
            if cite:
                lines.append(f'      <cite>{cite}</cite>')
            lines.append(f'    </blockquote>')
        lines.append(f'  </div>')

    lines.append("</section>")
    return "\n".join(lines)


def build_predictions_html(data: JSON) -> str:
    """Build the predictions summary table from all segments."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]

    all_predictions: list[dict[str, Any]] = []
    for seg in segments:
        for pred in seg.get("predictions", []):
            enriched = dict(pred)
            enriched["_segment_title"] = seg.get("title", "Unknown")
            all_predictions.append(enriched)

    if not all_predictions:
        return ""

    lines: list[str] = ['<section class="supplemental-section predictions-summary" aria-labelledby="predictions-heading">']
    lines.append('  <h2 id="predictions-heading">Predictions Summary</h2>')
    lines.append('  <table class="predictions-table">')
    lines.append('    <thead>')
    lines.append('      <tr>')
    lines.append('        <th>#</th>')
    lines.append('        <th>Prediction</th>')
    lines.append('        <th>Time Horizon</th>')
    lines.append('        <th>Confidence</th>')
    lines.append('        <th>From</th>')
    lines.append('        <th>Conditions</th>')
    lines.append('      </tr>')
    lines.append('    </thead>')
    lines.append('    <tbody>')

    for i, pred in enumerate(all_predictions, start=1):
        statement = esc(pred.get("statement", ""))
        horizon = esc(pred.get("time_horizon", "—"))
        confidence = pred.get("confidence", "medium")
        conf_label = esc(CONFIDENCE_LABELS.get(confidence, confidence))
        seg_title = esc(pred.get("_segment_title", ""))
        conditions = esc(pred.get("conditions", "—"))
        conf_css = CONFIDENCE_CSS.get(confidence, "conf-med")

        lines.append(f'      <tr>')
        lines.append(f'        <td class="pred-num">{i}</td>')
        lines.append(f'        <td class="pred-statement">{statement}</td>')
        lines.append(f'        <td>{horizon}</td>')
        lines.append(f'        <td><span class="pred-badge {esc(conf_css, quote=True)}">{conf_label}</span></td>')
        lines.append(f'        <td>{seg_title}</td>')
        lines.append(f'        <td class="pred-conditions">{conditions}</td>')
        lines.append(f'      </tr>')

    lines.append('    </tbody>')
    lines.append('  </table>')
    lines.append("</section>")
    return "\n".join(lines)


def build_themes_html(data: JSON) -> str:
    """Build the cross-cutting themes section with segment references."""
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]

    if not themes:
        return ""

    # Build a lookup from segment id to title
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
    seg_title_by_id: dict[str, str] = {}
    for seg in segments:
        seg_title_by_id[seg.get("id", "")] = seg.get("title", "Unknown")

    lines: list[str] = ['<section class="supplemental-section cross-themes" aria-labelledby="themes-heading">']
    lines.append('  <h2 id="themes-heading">Cross-Cutting Themes</h2>')

    for theme in themes:
        name = esc(theme.get("name", "Untitled Theme"))
        description = esc(theme.get("description", ""))
        refs: list[str] = theme.get("segment_refs", [])

        lines.append(f'  <div class="theme-block">')
        lines.append(f'    <h3>{name}</h3>')
        if description:
            lines.append(f'    <p>{description}</p>')

        if refs:
            lines.append(f'    <div class="theme-refs">')
            lines.append(f'      <span class="theme-ref-label">Appears in:</span>')
            for ref_id in refs:
                seg_title = esc(seg_title_by_id.get(ref_id, ref_id))
                section_id = make_section_id(ref_id)
                lines.append(f'      <a href="#{section_id}" class="theme-card">{seg_title}</a>')
            lines.append(f'    </div>')

        lines.append(f'  </div>')

    lines.append("</section>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core rendering
# ---------------------------------------------------------------------------


def read_template_files(template_dir: str) -> tuple[str, str, str]:
    """Read the three template files from the given directory.

    Args:
        template_dir: Path to assets/report-template/ directory.

    Returns:
        Tuple of (html_template, css_content, js_content).

    Raises:
        FileNotFoundError: If any template file is missing.
    """
    base = Path(template_dir)

    html_path = base / "index.html"
    css_path = base / "style.css"
    js_path = base / "script.js"

    missing: list[str] = []
    for p in (html_path, css_path, js_path):
        if not p.is_file():
            missing.append(str(p))

    if missing:
        raise FileNotFoundError(
            f"Template files not found: {', '.join(missing)}"
        )

    html_template = html_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8")
    js_content = js_path.read_text(encoding="utf-8")

    return html_template, css_content, js_content


def render_report(data: JSON, html_template: str, css_content: str, js_content: str) -> str:
    """Produce the final self-contained HTML report.

    Args:
        data: Parsed knowledge.json as a dict.
        html_template: Raw contents of index.html with template variables.
        css_content: Raw contents of style.css.
        js_content: Raw contents of script.js.

    Returns:
        Complete HTML document as a string.
    """
    # Build all content blocks
    title = build_title(data)
    metadata_html = build_metadata_html(data)
    sidebar_html = build_sidebar_html(data)
    content_html = build_content_html(data)
    quotes_html = build_quotes_html(data)
    predictions_html = build_predictions_html(data)
    themes_html = build_themes_html(data)

    # Inline CSS and JS
    # Replace the external stylesheet link with inline <style> blocks
    combined_css = css_content + "\n" + _SUPPLEMENTAL_CSS
    result = html_template.replace(
        '<link rel="stylesheet" href="style.css">',
        f"<style>\n{combined_css}\n</style>",
    )
    # Replace the external script tag with an inline <script> block
    result = result.replace(
        '<script src="script.js"></script>',
        f"<script>\n{js_content}\n</script>",
    )

    # Substitute template variables
    replacements: dict[str, str] = {
        "{{TITLE}}": title,
        "{{METADATA_HTML}}": metadata_html,
        "{{SIDEBAR_HTML}}": sidebar_html,
        "{{CONTENT_HTML}}": content_html,
        "{{QUOTES_HTML}}": quotes_html,
        "{{PREDICTIONS_HTML}}": predictions_html,
        "{{THEMES_HTML}}": themes_html,
    }

    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)

    return result


def load_knowledge_json(filepath: str) -> JSON:
    """Load and parse a knowledge.json file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Knowledge file not found: {filepath}")

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"Invalid JSON in {filepath}: {exc.msg}",
            exc.doc,
            exc.pos,
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object at the root of {filepath}, got {type(data).__name__}")

    return data


def write_output(html: str, output_path: str) -> None:
    """Write the rendered HTML to a file.

    Raises:
        OSError: If the file cannot be written.
    """
    try:
        out = Path(output_path)
        out.write_text(html, encoding="utf-8")
        print(f"Report written to: {out.resolve()}", file=sys.stderr)
    except OSError as exc:
        print(f"Error writing to {output_path}: {exc}", file=sys.stderr)
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Render an interactive HTML interview report from knowledge.json.",
    )
    parser.add_argument(
        "knowledge_json",
        metavar="KNOWLEDGE_JSON",
        help="Path to the knowledge.json input file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        default="report.html",
        help="Path for the output HTML file. Default: report.html",
    )
    parser.add_argument(
        "--template-dir",
        metavar="DIR",
        default=None,
        help="Path to the report-template directory. "
        "Default: ../assets/report-template/ relative to this script.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for the generate_html script."""
    parser = build_argparser()
    args = parser.parse_args(argv)

    # Resolve template directory
    if args.template_dir:
        template_dir = args.template_dir
    else:
        # Default: sibling assets/report-template/ relative to this script
        script_dir = Path(__file__).resolve().parent
        template_dir = str(script_dir.parent / "assets" / "report-template")

    # Load knowledge.json
    try:
        data = load_knowledge_json(args.knowledge_json)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Read template files
    try:
        html_template, css_content, js_content = read_template_files(template_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Render report
    try:
        html = render_report(data, html_template, css_content, js_content)
    except Exception as exc:
        print(f"Error rendering report: {exc}", file=sys.stderr)
        sys.exit(2)

    # Write output
    try:
        write_output(html, args.output)
    except OSError:
        sys.exit(1)


if __name__ == "__main__":
    main()
