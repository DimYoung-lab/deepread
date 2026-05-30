#!/usr/bin/env python3
"""Render a self-contained interactive HTML interview report from visual_content.json.

Reads a visual_content.json file (produced by Stage 4.5 visual synthesis),
combines it with the report-template assets (index.html, style.css, script.js),
and writes a single standalone HTML file with all CSS/JS inlined.

The HTML output uses a three-layer information architecture:
  Layer 1 "At a Glance"  -- Hero section with core thesis + key takeaways
  Layer 2 "The Argument"  -- Theme-organized narrative + curated evidence
  Layer 3 "The Evidence"  -- Complete timeline + predictions + quote collection

Supports automatic format detection:
  - visual_content.json (new): meta.core_thesis + themes[] + segments[]
  - knowledge.json (legacy fallback): metadata + segments[]

Usage:
    python generate_html.py visual_content.json
    python generate_html.py visual_content.json --output report.html
    python generate_html.py visual_content.json -o report.html --template-dir assets/report-template/
    python generate_html.py visual_content.json --knowledge knowledge.json   # predictions from knowledge.json

Template variables for visual_content format:
    {{HERO_HTML}}           -- core thesis, key takeaways, surprising insight, stats
    {{THEME_NAV_HTML}}      -- horizontal theme navigation tabs
    {{THEME_CONTENT_HTML}}  -- theme sections with narrative + argument cards + quotes
    {{TIMELINE_HTML}}       -- chronological segment browser
    {{PREDICTIONS_HTML}}    -- predictions summary table
    {{EVIDENCE_HTML}}       -- curated quotes organized by theme, collapsible

Template variables for legacy knowledge.json format:
    {{TITLE}}               -- interview title
    {{METADATA_HTML}}       -- header metadata
    {{SIDEBAR_HTML}}        -- sidebar navigation
    {{CONTENT_HTML}}        -- segment sections
    {{QUOTES_HTML}}         -- golden quotes collection
    {{PREDICTIONS_HTML}}    -- predictions table
    {{THEMES_HTML}}         -- cross-cutting themes
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
THEME_ID_PREFIX = "theme-"

# Supplemental CSS for generated content blocks not styled by the base template.
# Injected immediately after the template CSS in the final HTML.
# ALL font sizes use CSS custom properties (--fs-*) -- never hardcoded px/rem.
_SUPPLEMENTAL_CSS = r"""
/* ================================================================
   Generated Content Blocks -- supplemental styles
   ================================================================ */

/* ---- Hero Section ---- */
.hero-section {
  margin-bottom: var(--sp-3xl);
}

/* Core thesis */
.core-thesis {
  margin-bottom: var(--sp-2xl);
}
.thesis-statement {
  display: block; margin: 0 0 var(--sp-md) 0;
  padding: var(--sp-md) var(--sp-lg);
  font-size: var(--fs-lg); font-weight: 700;
  line-height: var(--lh-compact); color: var(--text-primary);
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 var(--r-md) var(--r-md) 0;
}
.thesis-elaboration {
  font-size: var(--fs-md); line-height: var(--lh-body);
  color: var(--text-secondary); max-width: var(--content-w, 72ch);
  margin: 0;
}

/* Stats bar */
.stats-bar {
  display: flex; flex-wrap: wrap; gap: var(--sp-sm);
  margin-bottom: var(--sp-xl);
}
.stat-badge {
  display: inline-flex; align-items: center; gap: var(--sp-xs);
  padding: var(--sp-sm) var(--sp-lg);
  font-family: var(--font-mono); font-size: var(--fs-sm);
  border-radius: var(--r-pill); white-space: nowrap;
  background: var(--accent-soft); color: var(--accent);
  border: 1px solid var(--border);
}
.stat-label {
  font-size: var(--fs-xs); text-transform: uppercase;
  letter-spacing: .04em; opacity: 0.7;
}
.stat-value {
  font-weight: 600;
}

/* Key takeaways grid */
.takeaways-grid {
  margin-bottom: var(--sp-2xl);
}
.takeaway-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--sp-md);
}
.takeaway-card {
  display: flex; gap: var(--sp-md); padding: var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface); transition: box-shadow var(--t-fast);
}
.takeaway-card:hover { box-shadow: var(--shadow-sm); }
.takeaway-number {
  font-family: var(--font-mono); font-size: var(--fs-lg);
  font-weight: 700; color: var(--accent);
  flex-shrink: 0; line-height: 1;
}
.takeaway-content { flex: 1; }
.takeaway-claim {
  font-weight: 600; font-size: var(--fs-base);
  line-height: var(--lh-compact); color: var(--text-primary);
  margin: 0 0 var(--sp-xs) 0;
}
.takeaway-elaboration {
  font-size: var(--fs-sm); line-height: var(--lh-compact);
  color: var(--text-secondary); margin: 0;
}

/* Most surprising insight callout */
.surprising-insight-callout {
  margin-bottom: var(--sp-2xl); padding: var(--sp-lg) var(--sp-xl);
  border: 1px solid var(--border);
  border-left: 4px solid #c4943a;
  border-radius: 0 var(--r-md) var(--r-md) 0;
  background: rgba(196,148,58,0.06);
}
.callout-label {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: #c4943a; text-transform: uppercase;
  letter-spacing: .05em; margin-bottom: var(--sp-sm);
}
.callout-claim {
  font-weight: 600; font-size: var(--fs-base);
  line-height: var(--lh-compact); color: var(--text-primary);
  margin: 0 0 var(--sp-sm) 0;
}
.callout-elaboration {
  font-size: var(--fs-sm); line-height: var(--lh-compact);
  color: var(--text-secondary); margin: 0 0 var(--sp-md) 0;
}
.callout-source {
  font-size: var(--fs-sm); font-style: italic;
  color: var(--text-muted); margin: 0; padding: 0;
  border: none; background: transparent;
}
.callout-source cite {
  display: inline-block; margin-left: var(--sp-sm);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  font-style: normal; color: var(--text-muted);
}

/* ---- Theme Navigation ---- */
.theme-nav {
  display: flex; flex-wrap: wrap; gap: var(--sp-xs);
  margin-bottom: var(--sp-2xl); padding-bottom: var(--sp-md);
  border-bottom: 2px solid var(--border);
  overflow-x: auto; -webkit-overflow-scrolling: touch;
}
.theme-tab {
  display: inline-block; padding: var(--sp-sm) var(--sp-lg);
  font-family: var(--font-mono); font-size: var(--fs-sm);
  color: var(--text-muted); background: transparent;
  border: 1px solid transparent; border-radius: var(--r-pill);
  cursor: pointer; white-space: nowrap;
  transition: color var(--t-fast), background var(--t-fast),
              border-color var(--t-fast);
  user-select: none;
}
.theme-tab:hover {
  color: var(--text-primary); background: var(--bg-alt);
  border-color: var(--border);
}
.theme-tab.active {
  color: var(--accent); background: var(--accent-soft);
  border-color: var(--accent); font-weight: 600;
}
.theme-tab.theme-tab--special {
  font-style: italic;
}

/* ---- Theme Content Sections ---- */
.theme-section {
  display: none; margin-bottom: var(--sp-3xl);
}
.theme-section.active { display: block; }
.theme-section .theme-heading {
  font-family: var(--font-heading); font-size: var(--fs-xl);
  line-height: var(--lh-compact); margin: 0 0 var(--sp-sm) 0;
}
.theme-summary {
  font-size: var(--fs-md); line-height: var(--lh-body);
  color: var(--text-secondary); margin-bottom: var(--sp-lg);
  font-style: italic;
}

/* Theme narrative */
.theme-narrative {
  font-size: var(--fs-base); line-height: var(--lh-body);
  color: var(--text-primary); max-width: var(--content-w, 72ch);
  margin-bottom: var(--sp-2xl);
}
.theme-narrative p { margin: 0 0 var(--sp-md) 0; }

/* Argument cards */
.theme-argument-cards { margin-bottom: var(--sp-2xl); }
.args-heading {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: .05em; margin-bottom: var(--sp-md);
}
.argument-card {
  margin: var(--sp-md) 0; padding: var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface); transition: box-shadow var(--t-fast);
}
.argument-card:hover { box-shadow: var(--shadow-sm); }
.argument-header {
  display: flex; align-items: center; gap: var(--sp-sm);
  margin-bottom: var(--sp-sm);
}
.importance-stars {
  font-size: var(--fs-sm); color: #c4943a;
  letter-spacing: .05em; user-select: none;
}
.argument-claim {
  font-weight: 600; font-size: var(--fs-base);
  line-height: var(--lh-compact); margin: 0 0 var(--sp-sm) 0;
  color: var(--text-primary);
}
.argument-explanation {
  font-size: var(--fs-sm); line-height: var(--lh-compact);
  color: var(--text-secondary); margin: 0 0 var(--sp-md) 0;
}
.argument-quote {
  margin: var(--sp-sm) 0 0 0; padding: var(--sp-sm) var(--sp-md);
  font-size: var(--fs-sm); font-style: italic;
  color: var(--text-muted);
  border-left: 3px solid var(--border);
  background: var(--bg-alt);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
}
.argument-quote cite {
  display: block; margin-top: var(--sp-xs);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  font-style: normal; color: var(--text-muted);
}

/* Theme quotes block */
.theme-quotes-block { margin-bottom: var(--sp-2xl); }
.theme-quotes-block .quotes-heading {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: .05em; margin-bottom: var(--sp-md);
}
.theme-quote {
  margin: var(--sp-md) 0; padding: var(--sp-md) var(--sp-lg);
  border-left: 3px solid var(--border-light);
  background: var(--bg-alt);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
}
.theme-quote p {
  font-size: var(--fs-base); line-height: var(--lh-body);
  margin: 0;
}
.theme-quote cite {
  display: block; margin-top: var(--sp-sm);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  font-style: normal; color: var(--text-muted);
}

/* Inline evidence toggle within theme sections */
.evidence-toggle {
  margin-top: var(--sp-lg);
  border-top: 1px solid var(--border-light);
  padding-top: var(--sp-md);
}
.evidence-toggle > summary {
  font-family: var(--font-mono); font-size: var(--fs-sm);
  color: var(--accent); cursor: pointer; user-select: none;
  display: inline-block;
}
.evidence-toggle > summary:hover { text-decoration: underline; }
.evidence-toggle .evidence-inline {
  margin-top: var(--sp-md);
}

/* ---- Timeline Section ---- */
.timeline-section {
  margin-bottom: var(--sp-3xl);
}
.timeline-section .section-heading {
  font-family: var(--font-heading); font-size: var(--fs-xl);
  margin: 0 0 var(--sp-lg) 0;
}
.timeline {
  position: relative; padding-left: var(--sp-2xl);
}
.timeline::before {
  content: ""; position: absolute; left: 8px; top: 0; bottom: 0;
  width: 2px; background: var(--border);
}
.timeline-item {
  position: relative; margin-bottom: var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface); transition: box-shadow var(--t-fast);
}
.timeline-item:hover { box-shadow: var(--shadow-sm); }
.timeline-item::before {
  content: ""; position: absolute;
  left: calc(-1 * var(--sp-2xl) + 4px);
  top: var(--sp-lg); width: 10px; height: 10px;
  border-radius: 50%; background: var(--accent);
  border: 2px solid var(--surface);
}
.timeline-item .timeline-header {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: var(--sp-sm);
  padding: var(--sp-md) var(--sp-lg) 0 var(--sp-lg);
}
.timeline-item .timeline-title {
  font-family: var(--font-heading); font-size: var(--fs-md);
  font-weight: 600; margin: 0; cursor: pointer;
}
.timeline-item .timeline-time {
  font-family: var(--font-mono); font-size: var(--fs-sm);
  color: var(--text-muted); white-space: nowrap;
}
.timeline-item .timeline-body {
  padding: 0 var(--sp-lg) var(--sp-lg) var(--sp-lg);
}
.timeline-item .synthesis-narrative {
  font-size: var(--fs-base); line-height: var(--lh-body);
  color: var(--text-secondary); margin: var(--sp-md) 0 0 0;
}
.timeline-item .timeline-theme-tags {
  display: flex; flex-wrap: wrap; gap: var(--sp-sm);
  margin-top: var(--sp-md);
}
.timeline-item .timeline-theme-tag {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  padding: 1px var(--sp-sm); border-radius: var(--r-pill);
  background: var(--accent-soft); color: var(--accent);
  border: 1px solid var(--border);
}
.timeline-item details[open] .timeline-body {
  display: block;
}

/* Segment highlight cards inside timeline */
.timeline-segment .insight-card {
  margin: var(--sp-sm) 0; padding: var(--sp-sm) var(--sp-md);
  border: 1px solid var(--border-light); border-radius: var(--r-sm);
  background: var(--bg-alt);
}
.timeline-segment .insight-header {
  display: flex; align-items: center; gap: var(--sp-sm);
  margin-bottom: var(--sp-xs);
}
.timeline-segment .insight-type-badge {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  padding: 1px var(--sp-sm); border-radius: var(--r-pill);
  background: var(--accent-soft); color: var(--accent);
  text-transform: uppercase; letter-spacing: .04em;
}
.timeline-segment .insight-claim {
  font-weight: 600; font-size: var(--fs-sm);
  line-height: var(--lh-compact);
}
.timeline-segment .insight-quote {
  margin: var(--sp-sm) 0; padding: var(--sp-sm) var(--sp-md);
  font-size: var(--fs-sm); font-style: italic;
  border-left: 3px solid var(--border-light);
  background: var(--bg-alt);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
}
.timeline-segment .insight-quote p { margin: 0; }
.timeline-segment .insight-quote cite {
  display: block; margin-top: var(--sp-xs);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  font-style: normal; color: var(--text-muted);
}

/* ---- Evidence Section ---- */
.evidence-section {
  margin-bottom: var(--sp-3xl);
}
.evidence-section .section-heading {
  font-family: var(--font-heading); font-size: var(--fs-xl);
  margin: 0 0 var(--sp-lg) 0;
}
.evidence-group {
  margin-bottom: var(--sp-lg);
}
.evidence-group > summary {
  font-family: var(--font-heading); font-size: var(--fs-md);
  font-weight: 600; cursor: pointer; user-select: none;
  padding: var(--sp-md) 0; color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}
.evidence-group > summary:hover { color: var(--accent); }
.evidence-group .evidence-quote {
  margin: var(--sp-md) 0; padding: var(--sp-md) var(--sp-lg);
  border-left: 3px solid var(--border-light);
  background: var(--bg-alt);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
}
.evidence-quote p {
  font-size: var(--fs-base); line-height: var(--lh-body);
  margin: 0;
}
.evidence-quote cite {
  display: block; margin-top: var(--sp-sm);
  font-family: var(--font-mono); font-size: var(--fs-xs);
  font-style: normal; color: var(--text-muted);
}
.evidence-quote-count {
  font-family: var(--font-mono); font-size: var(--fs-xs);
  color: var(--text-muted); font-weight: 400;
}

/* ---- Predictions table ---- */
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
.pred-conditions {
  font-size: var(--fs-xs); color: var(--text-muted); max-width: 18rem;
}
.prediction-confidence.conf-high { color: #4a9e6b; }
.prediction-confidence.conf-med  { color: #c4943a; }
.prediction-confidence.conf-low  { color: #c45a4a; }
.prediction-statement {
  font-weight: 600; font-size: var(--fs-base);
  margin-bottom: var(--sp-xs);
}
.prediction-horizon, .prediction-conditions {
  font-size: var(--fs-sm); color: var(--text-secondary);
}

/* ---- Legacy fallback styles ---- */
.segment-header {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: var(--sp-sm); margin-bottom: var(--sp-md);
}
.segment-time-range {
  font-family: var(--font-mono); font-size: var(--fs-sm);
  color: var(--text-muted); white-space: nowrap;
}
.segment-summary {
  font-size: var(--fs-base); line-height: var(--lh-body);
  color: var(--text-secondary); margin-bottom: var(--sp-lg);
}
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
.data-timestamp { margin-top: var(--sp-xs); }
.quote-group { margin-bottom: var(--sp-xl); }
.quote-group h3 {
  font-family: var(--font-heading); font-size: var(--fs-md);
  margin-bottom: var(--sp-md);
}
.theme-block {
  margin-bottom: var(--sp-xl); padding: var(--sp-lg);
  border: 1px solid var(--border-light); border-radius: var(--r-md);
  background: var(--surface);
}
.theme-refs {
  margin-top: var(--sp-md); display: flex; flex-wrap: wrap;
  gap: var(--sp-sm); align-items: center;
}
.theme-ref-label {
  font-size: var(--fs-sm); color: var(--text-muted);
}

/* Empty state */
.empty-message {
  color: var(--text-muted); font-style: italic;
  text-align: center; padding: var(--sp-3xl) var(--sp-xl);
}

/* ---- Responsive ---- */
@media (max-width: 640px) {
  .takeaway-cards { grid-template-columns: 1fr; }
  .theme-nav { gap: var(--sp-xs); padding-bottom: var(--sp-sm); }
  .theme-tab { padding: var(--sp-xs) var(--sp-md); font-size: var(--fs-xs); }
  .timeline { padding-left: var(--sp-xl); }
  .timeline-item::before {
    left: calc(-1 * var(--sp-xl) + 4px);
  }
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


def make_theme_section_id(theme_id: str) -> str:
    """Generate a stable HTML anchor id from a theme identifier."""
    return THEME_ID_PREFIX + _html.escape(theme_id, quote=True)


def _narrative_to_paragraphs(narrative: str) -> str:
    """Convert a narrative string with blank-line paragraph breaks into HTML <p> tags.

    Args:
        narrative: Raw narrative text, paragraphs separated by blank lines (\\n\\n).

    Returns:
        HTML string with <p> tags wrapping each paragraph.
    """
    if not narrative:
        return ""
    paragraphs = [p.strip() for p in narrative.strip().split("\n\n") if p.strip()]
    if not paragraphs:
        return f"<p>{esc(narrative.strip())}</p>"
    return "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)


def _render_importance_stars(importance: int) -> str:
    """Render importance as star characters (1-5 scale).

    Args:
        importance: Importance value (1-5). Clamped to 1-5.

    Returns:
        HTML span with filled/empty star characters and a title attribute.
    """
    stars_val = max(1, min(5, int(importance)))
    filled = "★" * stars_val       # black star
    empty = "☆" * (5 - stars_val)  # white star
    return (
        f'<span class="importance-stars" '
        f'title="Importance: {stars_val}/5">{filled}{empty}</span>'
    )


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------


def _is_visual_content_format(data: JSON) -> bool:
    """Detect whether the JSON uses the visual_content.json schema.

    Checks for meta.core_thesis and a top-level themes list.
    """
    if not isinstance(data, dict):
        return False
    meta = data.get("meta")
    themes = data.get("themes")
    return (
        isinstance(meta, dict)
        and isinstance(themes, list)
        and bool(meta.get("core_thesis"))
    )


def detect_data_format(data: JSON) -> str:
    """Detect which data format the JSON uses.

    Returns:
        "visual_content" -- has meta.core_thesis + themes[].
        "knowledge"      -- has metadata dict (legacy).
        "unknown"        -- neither recognised.
    """
    if _is_visual_content_format(data):
        return "visual_content"
    if isinstance(data, dict) and isinstance(data.get("metadata"), dict):
        return "knowledge"
    return "unknown"


# ---------------------------------------------------------------------------
# Hero Section Builder  (Layer 1: At a Glance)
# ---------------------------------------------------------------------------


def build_hero_html(data: JSON) -> str:
    """Build the hero section: core thesis, key takeaways, surprising insight, stats.

    Produces:
        - Core thesis as a prominent blockquote
        - Thesis elaboration paragraph
        - Stats bar with badges
        - Key takeaways as a grid of numbered cards
        - Most-surprising-insight callout box

    Args:
        data: Parsed visual_content.json dict.

    Returns:
        HTML string for the hero section, or empty string if no meta.
    """
    if not isinstance(data, dict):
        return ""

    meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    lines: list[str] = []
    lines.append('<section class="hero-section" aria-labelledby="hero-heading">')

    # -- Core thesis --
    core_thesis = meta.get("core_thesis", "")
    core_elaboration = meta.get("core_thesis_elaboration", "")
    if core_thesis:
        lines.append('  <div class="core-thesis">')
        lines.append(f'    <h2 class="section-label" id="hero-heading">Core Thesis</h2>')
        lines.append(f'    <blockquote class="thesis-statement">{esc(core_thesis)}</blockquote>')
        if core_elaboration:
            lines.append(f'    <p class="thesis-elaboration">{esc(core_elaboration)}</p>')
        lines.append('  </div>')

    # -- Stats bar --
    stats: dict[str, Any] = meta.get("stats", {})
    if stats:
        lines.append('  <div class="stats-bar">')
        stat_defs = [
            ("duration_formatted", "Duration"),
            ("segment_count", "Segments"),
            ("insight_count", "Insights"),
            ("quote_count", "Quotes"),
            ("prediction_count", "Predictions"),
            ("theme_count", "Themes"),
        ]
        for key, label in stat_defs:
            value = stats.get(key)
            if value is not None and value != "":
                lines.append(
                    f'    <span class="stat-badge">'
                    f'<span class="stat-label">{esc(label)}</span> '
                    f'<span class="stat-value">{esc(str(value))}</span>'
                    f'</span>'
                )
        lines.append('  </div>')

    # -- Key takeaways grid --
    takeaways: list[dict[str, Any]] = meta.get("key_takeaways", [])
    if takeaways:
        lines.append('  <div class="takeaways-grid">')
        lines.append('    <h2 class="section-label">Key Takeaways</h2>')
        lines.append('    <div class="takeaway-cards">')
        for i, tk in enumerate(takeaways, start=1):
            claim = esc(tk.get("claim", ""))
            elaboration = esc(tk.get("elaboration", ""))
            num_str = f"{i:02d}"
            lines.append('      <div class="takeaway-card">')
            lines.append(f'        <span class="takeaway-number">{num_str}</span>')
            lines.append('        <div class="takeaway-content">')
            lines.append(f'          <p class="takeaway-claim">{claim}</p>')
            if elaboration:
                lines.append(f'          <p class="takeaway-elaboration">{elaboration}</p>')
            lines.append('        </div>')
            lines.append('      </div>')
        lines.append('    </div>')
        lines.append('  </div>')

    # -- Most surprising insight callout --
    surprising: dict[str, Any] = meta.get("most_surprising_insight", {})  # type: ignore[assignment]
    if isinstance(surprising, dict) and surprising.get("claim"):
        lines.append('  <div class="surprising-insight-callout">')
        lines.append('    <div class="callout-label">Most Surprising Insight</div>')
        lines.append(f'    <p class="callout-claim">{esc(surprising["claim"])}</p>')
        if surprising.get("elaboration"):
            lines.append(f'    <p class="callout-elaboration">{esc(surprising["elaboration"])}</p>')
        sq = surprising.get("source_quote", {})
        if isinstance(sq, dict) and sq.get("text"):
            lines.append(
                f'    <blockquote class="callout-source">'
                f'{esc(sq["text"])}'
                f'<cite>{esc(sq.get("timestamp", ""))}</cite>'
                f'</blockquote>'
            )
        lines.append('  </div>')

    lines.append('</section>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Theme Navigation Builder
# ---------------------------------------------------------------------------


def build_theme_nav_html(data: JSON) -> str:
    """Build horizontal theme navigation tabs + Timeline + All Evidence tabs.

    The first theme tab is marked active by default.  The JS in the template
    should wire clicks to show/hide the corresponding content sections.

    Args:
        data: Parsed visual_content.json dict.

    Returns:
        HTML string for the <nav> element, or empty string if no themes.
    """
    if not isinstance(data, dict):
        return ""

    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    if not themes:
        return ""

    lines: list[str] = ['<nav class="theme-nav" aria-label="Theme navigation">']

    for i, theme in enumerate(themes):
        tid = theme.get("id", f"theme_{i}")
        name = esc(theme.get("name", f"Theme {i + 1}"))
        active = ' active' if i == 0 else ''
        lines.append(
            f'  <button class="theme-tab{active}" '
            f'data-theme="{esc(tid, quote=True)}" '
            f'aria-selected="{str(i == 0).lower()}">{name}</button>'
        )

    # Special tabs for Timeline and Evidence sections
    lines.append(
        '  <button class="theme-tab theme-tab--special" '
        'data-section="timeline">Timeline</button>'
    )
    lines.append(
        '  <button class="theme-tab theme-tab--special" '
        'data-section="evidence">All Evidence</button>'
    )

    lines.append('</nav>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Theme Content Builder  (Layer 2: The Argument)
# ---------------------------------------------------------------------------


def build_theme_content_html(data: JSON) -> str:
    """Build the main content area with theme sections.

    Each theme section contains:
      - Theme name as heading
      - Summary as italic lede
      - Narrative prose (blank-line separated paragraphs)
      - Argument cards for each highlighted_insight (with importance stars)
      - Blockquotes for highlighted_quotes
      - Collapsible "Browse All Evidence" toggle at the bottom

    The first theme section is marked active.

    Args:
        data: Parsed visual_content.json dict.

    Returns:
        HTML string for all theme content sections.
    """
    if not isinstance(data, dict):
        return ""

    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    curated_quotes: list[dict[str, Any]] = data.get("curated_quotes", [])  # type: ignore[assignment]

    if not themes:
        return '<p class="empty-message">No themes to display.</p>'

    # Index curated quotes by theme for the inline evidence toggle
    quotes_by_theme: dict[str, list[dict[str, Any]]] = {}
    for cq in curated_quotes:
        belongs = cq.get("belongs_to_theme", "")
        if belongs:
            quotes_by_theme.setdefault(belongs, []).append(cq)

    # Build theme name lookup for related-theme links
    theme_names: dict[str, str] = {}
    for t in themes:
        theme_names[t.get("id", "")] = t.get("name", t.get("id", "Unknown"))

    sections: list[str] = []
    for i, theme in enumerate(themes):
        sections.append(_render_theme_section(theme, i, quotes_by_theme, theme_names))

    lines: list[str] = ['<div class="theme-sections" id="theme-sections">']
    lines.append("\n\n".join(sections))
    lines.append('</div>')
    return "\n".join(lines)


def _render_theme_section(
    theme: dict[str, Any],
    index: int,
    quotes_by_theme: dict[str, list[dict[str, Any]]],
    theme_names: dict[str, str],
) -> str:
    """Render a single theme section."""

    tid = theme.get("id", f"theme_{index}")
    name = esc(theme.get("name", f"Theme {index + 1}"))
    summary = esc(theme.get("summary", ""))
    narrative = theme.get("narrative", "")
    section_id = make_theme_section_id(tid)
    active_class = " active" if index == 0 else ""

    lines: list[str] = []
    lines.append(
        f'<section class="theme-section{active_class}" '
        f'id="{section_id}" data-theme="{esc(tid, quote=True)}" '
        f'aria-labelledby="heading-{section_id}">'
    )

    # Heading + summary
    lines.append(f'  <h2 class="theme-heading" id="heading-{section_id}">{name}</h2>')
    if summary:
        lines.append(f'  <p class="theme-summary">{summary}</p>')

    # Narrative prose
    if narrative:
        lines.append('  <div class="theme-narrative">')
        lines.append(_narrative_to_paragraphs(narrative))
        lines.append('  </div>')

    # Argument cards for highlighted insights
    insights: list[dict[str, Any]] = theme.get("highlighted_insights", [])
    if insights:
        lines.append('  <div class="theme-argument-cards">')
        lines.append('    <h3 class="args-heading">Key Arguments</h3>')
        for ins in insights:
            lines.append(_render_argument_card(ins))
        lines.append('  </div>')

    # Highlighted quotes
    hquotes: list[dict[str, Any]] = theme.get("highlighted_quotes", [])
    if hquotes:
        lines.append('  <div class="theme-quotes-block">')
        lines.append('    <h3 class="quotes-heading">Notable Quotes</h3>')
        for q in hquotes:
            lines.append(_render_theme_quote(q))
        lines.append('  </div>')

    # Related themes
    related: list[str] = theme.get("related_themes", [])
    if related:
        lines.append('  <div class="theme-refs">')
        lines.append(
            '    <span class="theme-ref-label">Related themes:</span>'
        )
        for rt in related:
            rt_name = esc(theme_names.get(rt, rt))
            lines.append(
                f'    <a href="#{make_theme_section_id(rt)}" '
                f'class="topic-tag">{rt_name}</a>'
            )
        lines.append('  </div>')

    # Browse All Evidence inline toggle
    theme_quotes = quotes_by_theme.get(tid, [])
    if theme_quotes:
        lines.append('  <details class="evidence-toggle">')
        lines.append(
            f'    <summary>Browse All Evidence '
            f'<span class="evidence-quote-count">({len(theme_quotes)} quotes)</span>'
            f'</summary>'
        )
        lines.append('    <div class="evidence-inline">')
        for eq in theme_quotes:
            lines.append(_render_evidence_quote(eq))
        lines.append('    </div>')
        lines.append('  </details>')

    lines.append('</section>')
    return "\n".join(lines)


def _render_argument_card(insight: dict[str, Any]) -> str:
    """Render a highlighted insight as an argument card with importance stars.

    Args:
        insight: Dict with claim, explanation, importance, source_segments,
                 key_quote, related_data_points.

    Returns:
        HTML string for the argument card.
    """
    claim = esc(insight.get("claim", ""))
    explanation = esc(insight.get("explanation", ""))
    importance = insight.get("importance", 3)
    key_quote = insight.get("key_quote")

    lines: list[str] = []
    lines.append('    <div class="argument-card">')
    lines.append('      <div class="argument-header">')
    lines.append(f'        {_render_importance_stars(int(importance))}')
    lines.append('      </div>')
    if claim:
        lines.append(f'      <p class="argument-claim">{claim}</p>')
    if explanation:
        lines.append(f'      <p class="argument-explanation">{explanation}</p>')
    if isinstance(key_quote, dict) and key_quote.get("text"):
        kq_text = esc(key_quote["text"])
        kq_ts = key_quote.get("timestamp", "")
        kq_speaker = key_quote.get("speaker", "")
        lines.append('      <blockquote class="argument-quote">')
        lines.append(f'        {kq_text}')
        cite_parts: list[str] = []
        if kq_ts:
            cite_parts.append(esc(kq_ts))
        if kq_speaker:
            cite_parts.append(esc(kq_speaker))
        if cite_parts:
            lines.append(f'        <cite>{" — ".join(cite_parts)}</cite>')
        lines.append('      </blockquote>')
    lines.append('    </div>')
    return "\n".join(lines)


def _render_theme_quote(quote: dict[str, Any]) -> str:
    """Render a highlighted quote as a blockquote within a theme section.

    Args:
        quote: Dict with text, timestamp, speaker, context_note.

    Returns:
        HTML string for the blockquote.
    """
    text = esc(quote.get("text", ""))
    ts = quote.get("timestamp", "")
    speaker = quote.get("speaker", "")
    context_note = esc(quote.get("context_note", ""))

    lines: list[str] = []
    lines.append(
        f'    <blockquote class="theme-quote" '
        f'data-timestamp="{esc(ts, quote=True)}">'
    )
    lines.append(f'      <p>{text}</p>')
    cite_parts: list[str] = []
    if ts:
        cite_parts.append(timestamp_badge(ts))
    if speaker:
        cite_parts.append(esc(speaker))
    if context_note:
        cite_parts.append(context_note)
    if cite_parts:
        lines.append(f'      <cite>{" — ".join(cite_parts)}</cite>')
    lines.append('    </blockquote>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Timeline Builder  (Layer 3: Chronological segment browser)
# ---------------------------------------------------------------------------


def build_timeline_html(data: JSON) -> str:
    """Build a collapsible chronological segment browser from data.segments.

    Each segment renders as a <details> element on a vertical timeline,
    showing title, time range, synthesis_narrative, theme tags, and any
    highlighted insights/quotes.

    Args:
        data: Parsed visual_content.json dict.

    Returns:
        HTML string for the timeline section.
    """
    if not isinstance(data, dict):
        return ""

    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
    if not segments:
        return ""

    # Theme name lookup for tagging
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    theme_name_by_id: dict[str, str] = {}
    for t in themes:
        theme_name_by_id[t.get("id", "")] = t.get("name", "Unknown")

    lines: list[str] = []
    lines.append(
        '<section class="timeline-section" id="section-timeline" '
        'aria-labelledby="timeline-heading">'
    )
    lines.append(
        '  <h2 class="section-heading" id="timeline-heading">'
        'Conversation Timeline</h2>'
    )
    lines.append('  <div class="timeline">')

    for i, seg in enumerate(segments):
        lines.append(_render_timeline_item(seg, i, theme_name_by_id))

    lines.append('  </div>')
    lines.append('</section>')
    return "\n".join(lines)


def _render_timeline_item(
    seg: dict[str, Any],
    index: int,
    theme_name_by_id: dict[str, str],
) -> str:
    """Render a single segment as a timeline item (collapsible <details>)."""
    seg_id = seg.get("id", f"seg_{index}")
    title = esc(seg.get("title", f"Segment {index + 1}"))
    time_range = seg.get("time_range", {})
    start = time_range.get("start", "") if isinstance(time_range, dict) else ""
    end = time_range.get("end", "") if isinstance(time_range, dict) else ""
    narrative = seg.get("synthesis_narrative", "")
    belongs_to: list[str] = seg.get("belongs_to_themes", [])
    section_id = make_section_id(seg_id)

    lines: list[str] = []
    lines.append(
        f'    <details class="timeline-item timeline-segment" '
        f'id="{section_id}" data-segment-id="{esc(seg_id, quote=True)}">'
    )

    # Summary (always visible): title + time
    lines.append('      <summary class="timeline-header">')
    lines.append(f'        <span class="timeline-title">{title}</span>')
    if start and end:
        lines.append(
            f'        <span class="timeline-time">{esc(start)} – {esc(end)}</span>'
        )
    elif start:
        lines.append(f'        <span class="timeline-time">{esc(start)}</span>')
    lines.append('      </summary>')

    # Body (expandable)
    lines.append('      <div class="timeline-body">')
    if narrative:
        lines.append(f'        <p class="synthesis-narrative">{esc(narrative)}</p>')

    # Theme tags
    if belongs_to:
        lines.append('        <div class="timeline-theme-tags">')
        for tid in belongs_to:
            tname = esc(theme_name_by_id.get(tid, tid))
            lines.append(
                f'          <a href="#{make_theme_section_id(tid)}" '
                f'class="timeline-theme-tag">{tname}</a>'
            )
        lines.append('        </div>')

    # Highlighted insights from this segment
    seg_insights: list[dict[str, Any]] = seg.get("highlighted_insights", [])
    for ins in seg_insights:
        claim = esc(ins.get("claim", ""))
        ins_type = esc(ins.get("type", ""))
        ts = ins.get("timestamp", "")
        lines.append('        <div class="insight-card">')
        lines.append('          <div class="insight-header">')
        if ins_type:
            lines.append(f'            <span class="insight-type-badge">{ins_type}</span>')
        if ts:
            lines.append(f'            {timestamp_badge(ts)}')
        lines.append('          </div>')
        lines.append(f'          <div class="insight-claim">{claim}</div>')
        lines.append('        </div>')

    # Highlighted quotes from this segment
    seg_quotes: list[dict[str, Any]] = seg.get("highlighted_quotes", [])
    for sq in seg_quotes:
        sq_text = esc(sq.get("text", ""))
        sq_ts = sq.get("timestamp", "")
        sq_speaker = sq.get("speaker", "")
        lines.append(
            f'        <blockquote class="insight-quote" '
            f'data-timestamp="{esc(sq_ts, quote=True)}">'
        )
        lines.append(f'          <p>{sq_text}</p>')
        cite_parts: list[str] = []
        if sq_ts:
            cite_parts.append(timestamp_badge(sq_ts))
        if sq_speaker:
            cite_parts.append(esc(sq_speaker))
        if cite_parts:
            lines.append(f'          <cite>{" — ".join(cite_parts)}</cite>')
        lines.append('        </blockquote>')

    lines.append('      </div>')
    lines.append('    </details>')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Evidence Collection Builder  (Layer 3: Curated Quotes)
# ---------------------------------------------------------------------------


def build_evidence_html(data: JSON) -> str:
    """Build the evidence section with curated_quotes organized by theme.

    Each theme group is a collapsible <details> element.  Groups appear
    in the same order as data.themes, with quotes sorted within each group.

    Args:
        data: Parsed visual_content.json dict.

    Returns:
        HTML string for the evidence section, or empty string if no quotes.
    """
    if not isinstance(data, dict):
        return ""

    curated_quotes: list[dict[str, Any]] = data.get("curated_quotes", [])  # type: ignore[assignment]
    if not curated_quotes:
        return ""

    # Theme name lookup
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    theme_name_by_id: dict[str, str] = {}
    theme_order: list[str] = []
    for t in themes:
        tid = t.get("id", "")
        theme_name_by_id[tid] = t.get("name", tid)
        theme_order.append(tid)

    # Group quotes by theme
    quotes_by_theme: dict[str, list[dict[str, Any]]] = {}
    unassigned: list[dict[str, Any]] = []
    for cq in curated_quotes:
        bt = cq.get("belongs_to_theme", "")
        if bt:
            quotes_by_theme.setdefault(bt, []).append(cq)
        else:
            unassigned.append(cq)

    lines: list[str] = []
    lines.append(
        '<section class="evidence-section" id="section-evidence" '
        'aria-labelledby="evidence-heading">'
    )
    lines.append(
        '  <h2 class="section-heading" id="evidence-heading">'
        f'All Evidence ({len(curated_quotes)} quotes)</h2>'
    )

    # Render in theme order
    for tid in theme_order:
        group = quotes_by_theme.get(tid, [])
        if not group:
            continue
        tname = esc(theme_name_by_id.get(tid, tid))
        lines.append('  <details class="evidence-group" open>')
        lines.append(
            f'    <summary>{tname} '
            f'<span class="evidence-quote-count">({len(group)})</span></summary>'
        )
        for eq in group:
            lines.append(_render_evidence_quote(eq))
        lines.append('  </details>')

    # Any remaining themes not in theme_order
    for tid, group in quotes_by_theme.items():
        if tid in theme_order:
            continue
        tname = esc(theme_name_by_id.get(tid, tid))
        lines.append('  <details class="evidence-group">')
        lines.append(
            f'    <summary>{tname} '
            f'<span class="evidence-quote-count">({len(group)})</span></summary>'
        )
        for eq in group:
            lines.append(_render_evidence_quote(eq))
        lines.append('  </details>')

    # Unassigned quotes
    if unassigned:
        lines.append('  <details class="evidence-group">')
        lines.append(
            f'    <summary>Other '
            f'<span class="evidence-quote-count">({len(unassigned)})</span></summary>'
        )
        for eq in unassigned:
            lines.append(_render_evidence_quote(eq))
        lines.append('  </details>')

    lines.append('</section>')
    return "\n".join(lines)


def _render_evidence_quote(quote: dict[str, Any]) -> str:
    """Render a single curated quote as a blockquote for the evidence section.

    Args:
        quote: Dict with text, timestamp, speaker, context_note.

    Returns:
        HTML string for the evidence quote block.
    """
    text = esc(quote.get("text", ""))
    ts = quote.get("timestamp", "")
    speaker = quote.get("speaker", "")
    context_note = esc(quote.get("context_note", ""))

    lines: list[str] = []
    lines.append('    <blockquote class="evidence-quote">')
    lines.append(f'      <p>{text}</p>')
    cite_parts: list[str] = []
    if ts:
        cite_parts.append(timestamp_badge(ts))
    if speaker:
        cite_parts.append(esc(speaker))
    if context_note:
        cite_parts.append(context_note)
    if cite_parts:
        lines.append(f'      <cite>{" — ".join(cite_parts)}</cite>')
    lines.append('    </blockquote>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Predictions Builder
# ---------------------------------------------------------------------------


def build_predictions_html(data: JSON, knowledge_data: JSON | None = None) -> str:
    """Build the predictions summary table.

    Tries knowledge_data segments first (if provided), then falls back to
    looking for predictions in data.segments (visual_content format).

    Args:
        data: Primary JSON data (visual_content.json).
        knowledge_data: Optional knowledge.json for predictions fallback.

    Returns:
        HTML string for the predictions table, or empty string if none.
    """
    all_predictions: list[dict[str, Any]] = []

    # Try knowledge.json segments first
    if knowledge_data:
        ksegments = knowledge_data.get("segments", []) if isinstance(knowledge_data, dict) else []
        for seg in ksegments:
            for pred in seg.get("predictions", []):
                enriched = dict(pred)
                enriched["_segment_title"] = seg.get("title", "Unknown")
                all_predictions.append(enriched)

    # Fall back: try segments in primary data
    if not all_predictions and isinstance(data, dict):
        segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
        for seg in segments:
            for pred in seg.get("predictions", []):
                enriched = dict(pred)
                enriched["_segment_title"] = seg.get("title", "Unknown")
                all_predictions.append(enriched)

    if not all_predictions:
        return ""

    lines: list[str] = [
        '<section class="evidence-section" aria-labelledby="predictions-heading">'
    ]
    lines.append('  <h2 class="section-heading" id="predictions-heading">'
                 'Predictions Summary</h2>')
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
        statement = esc(pred.get("prediction", pred.get("statement", "")))
        horizon = esc(pred.get("time_horizon", "—"))
        confidence = pred.get("confidence", "medium")
        conf_label = esc(CONFIDENCE_LABELS.get(confidence, confidence))
        seg_title = esc(pred.get("_segment_title", ""))
        conditions = esc(pred.get("conditions", "—"))
        conf_css = CONFIDENCE_CSS.get(confidence, "conf-med")

        lines.append('      <tr>')
        lines.append(f'        <td class="pred-num">{i}</td>')
        lines.append(f'        <td class="pred-statement">{statement}</td>')
        lines.append(f'        <td>{horizon}</td>')
        lines.append(
            f'        <td><span class="pred-badge {esc(conf_css, quote=True)}">'
            f'{conf_label}</span></td>'
        )
        lines.append(f'        <td>{seg_title}</td>')
        lines.append(f'        <td class="pred-conditions">{conditions}</td>')
        lines.append('      </tr>')

    lines.append('    </tbody>')
    lines.append('  </table>')
    lines.append('</section>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Legacy (knowledge.json) builders  -- kept for backward compatibility
# ---------------------------------------------------------------------------


def build_title_legacy(data: JSON) -> str:
    """Extract report title from knowledge.json metadata."""
    meta: dict[str, Any] = data.get("metadata", {})  # type: ignore[assignment]
    return esc(meta.get("title", "Interview Report"))


def build_metadata_html_legacy(data: JSON) -> str:
    """Build metadata line from knowledge.json."""
    meta: dict[str, Any] = data.get("metadata", {})  # type: ignore[assignment]
    segments: list[Any] = data.get("segments", [])  # type: ignore[assignment]

    pieces: list[str] = []

    guest = meta.get("guest", {})
    if isinstance(guest, dict) and guest.get("name"):
        name = guest["name"]
        aff = guest.get("affiliation", "")
        if aff:
            pieces.append(f'<span class="meta-guest">{esc(name)}, {esc(aff)}</span>')
        else:
            pieces.append(f'<span class="meta-guest">{esc(name)}</span>')

    interviewer = meta.get("interviewer", {})
    if isinstance(interviewer, dict) and interviewer.get("name"):
        pieces.append(
            f'<span class="meta-host">Host: {esc(interviewer["name"])}</span>'
        )

    if meta.get("date"):
        pieces.append(f'<span class="meta-date">{esc(str(meta["date"]))}</span>')

    duration = (
        meta.get("duration_seconds") or meta.get("total_duration_seconds") or 0
    )
    if duration:
        pieces.append(
            f'<span class="meta-duration">'
            f'{esc(format_duration(int(duration)))}</span>'
        )

    if segments:
        pieces.append(f'<span class="meta-stat">{len(segments)} segments</span>')

    total_quotes = sum(len(s.get("golden_quotes", [])) for s in segments)
    total_preds = sum(len(s.get("predictions", [])) for s in segments)
    if total_quotes:
        pieces.append(f'<span class="meta-stat">{total_quotes} quotes</span>')
    if total_preds:
        pieces.append(f'<span class="meta-stat">{total_preds} predictions</span>')

    return "\n        ".join(pieces)


def build_sidebar_html_legacy(data: JSON) -> str:
    """Build sidebar navigation from knowledge.json segments."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
    if not segments:
        return "<nav><ul><li><em>No segments found.</em></li></ul></nav>"

    items: list[str] = ["<nav><ul>"]
    for seg in segments:
        sid = seg.get("id", "")
        title = esc(seg.get("title", "Untitled"))
        tr = seg.get("time_range", {})
        start = tr.get("start", "") if isinstance(tr, dict) else ""
        section_id = make_section_id(sid)
        label = title
        if start:
            label += f" <small>{esc(start)}</small>"
        items.append(f'  <li><a href="#{section_id}">{label}</a></li>')
    items.append("</ul></nav>")
    return "\n".join(items)


def build_content_html_legacy(data: JSON) -> str:
    """Build main content from knowledge.json segments."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
    if not segments:
        return '<p class="empty-message">No segments to display.</p>'

    sections: list[str] = []
    for seg in segments:
        sections.append(_render_segment_legacy(seg))
    return "\n\n".join(sections)


def _render_segment_legacy(seg: dict[str, Any]) -> str:
    """Render a single segment as collapsible <details> (legacy format)."""
    sid = seg.get("id", "")
    title = esc(seg.get("title", "Untitled"))
    section_id = make_section_id(sid)

    tr = seg.get("time_range", {})
    time_start = tr.get("start", "") if isinstance(tr, dict) else ""
    time_end = tr.get("end", "") if isinstance(tr, dict) else ""

    lines: list[str] = []
    lines.append(
        f'<details open id="{section_id}" class="segment-details" '
        f'data-segment-id="{esc(sid, quote=True)}" '
        f'aria-labelledby="heading-{section_id}">'
    )

    time_range_html = (
        f"{esc(time_start)} – {esc(time_end)}"
        if time_start and time_end
        else ""
    )
    lines.append('  <summary class="segment-header">')
    lines.append(f'    <h2 id="heading-{section_id}">{title}</h2>')
    if time_range_html:
        lines.append(f'    <span class="segment-time-range">{time_range_html}</span>')
    lines.append('  </summary>')

    summary = seg.get("summary", "")
    if summary:
        lines.append(f'  <p class="segment-summary">{esc(summary)}</p>')

    key_topics: list[str] = seg.get("key_topics", [])
    if key_topics:
        tags = "\n".join(
            f'    <span class="topic-tag">{esc(t)}</span>' for t in key_topics
        )
        lines.append('  <div class="key-topics">')
        lines.append(tags)
        lines.append('  </div>')

    # Insights
    for ins in seg.get("insights", []):
        claim = esc(ins.get("claim", ""))
        explanation = esc(ins.get("explanation", ""))
        ins_type = esc(ins.get("type", ""))
        ts = ins.get("timestamp", "")
        lines.append('    <div class="insight-card">')
        lines.append('      <div class="insight-header">')
        if ins_type:
            lines.append(f'        <span class="insight-type-badge">{ins_type}</span>')
        if ts:
            lines.append(f'        {timestamp_badge(ts)}')
        lines.append('      </div>')
        lines.append(f'      <div class="insight-claim">{claim}</div>')
        if explanation:
            lines.append(f'      <div class="insight-explanation">{explanation}</div>')
        lines.append('    </div>')

    # Golden quotes
    for q in seg.get("golden_quotes", []):
        text = esc(q.get("text", ""))
        ts = q.get("timestamp", "")
        ctx = esc(q.get("context", ""))
        lines.append(
            f'    <blockquote class="insight-quote" '
            f'data-timestamp="{esc(ts, quote=True)}">'
        )
        lines.append(f'      <p>{text}</p>')
        cite_parts = []
        if ts:
            cite_parts.append(timestamp_badge(ts))
        if ctx:
            cite_parts.append(ctx)
        if cite_parts:
            lines.append(f'      <cite>{" — ".join(cite_parts)}</cite>')
        lines.append('    </blockquote>')

    # Data points
    for dp in seg.get("data_points", []):
        label = esc(dp.get("label", ""))
        value = esc(dp.get("value", ""))
        note = esc(dp.get("note", ""))
        dp_type = dp.get("type", "statistic")
        ts = dp.get("timestamp", "")
        css_class = DATA_TYPE_CSS.get(dp_type, "type-green")
        icon = DATA_TYPE_ICONS.get(dp_type, "?")
        lines.append(f'    <div class="data-point {esc(css_class, quote=True)}">')
        lines.append(f'      <div class="data-label">{icon} {esc(dp_type)}</div>')
        lines.append(f'      <div class="data-value">{label}: {value}</div>')
        if note:
            lines.append(f'      <div class="data-note">{note}</div>')
        if ts:
            lines.append(f'      <div class="data-timestamp">{timestamp_badge(ts)}</div>')
        lines.append('    </div>')

    # Contradictions
    for ct in seg.get("contradictions", []):
        stmt = esc(ct.get("statement", ""))
        ctx = esc(ct.get("context", ""))
        ts = ct.get("timestamp", "")
        lines.append('    <div class="contradiction-callout">')
        lines.append('      <div class="contradiction-label">Tension / Open Question</div>')
        lines.append(f'      <p>{stmt}</p>')
        if ctx:
            lines.append(f'      <p class="contradiction-context">{ctx}</p>')
        if ts:
            lines.append(f'      {timestamp_badge(ts)}')
        lines.append('    </div>')

    # Predictions
    for pred in seg.get("predictions", []):
        stmt = esc(pred.get("statement", ""))
        horizon = esc(pred.get("time_horizon", ""))
        confidence = pred.get("confidence", "medium")
        conditions = esc(pred.get("conditions", ""))
        conf_label = CONFIDENCE_LABELS.get(confidence, confidence)
        conf_css = CONFIDENCE_CSS.get(confidence, "conf-med")
        lines.append('    <div class="prediction-item">')
        lines.append(
            f'      <div class="prediction-confidence {esc(conf_css, quote=True)}">'
            f'{esc(conf_label)}</div>'
        )
        lines.append(f'      <div class="prediction-statement">{stmt}</div>')
        if horizon:
            lines.append(f'      <div class="prediction-horizon">Time horizon: {horizon}</div>')
        if conditions:
            lines.append(f'      <div class="prediction-conditions">Conditions: {conditions}</div>')
        lines.append('    </div>')

    lines.append("</details>")
    return "\n".join(lines)


def build_quotes_html_legacy(data: JSON) -> str:
    """Build gold-quote collection grouped by segment (legacy)."""
    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]

    collected: list[tuple[str, str, list[dict[str, Any]]]] = []
    for seg in segments:
        quotes = seg.get("golden_quotes", [])
        if quotes:
            collected.append(
                (seg.get("title", "Unknown"), esc(seg.get("id", "")), quotes)
            )

    if not collected:
        return ""

    lines: list[str] = [
        '<section class="supplemental-section quotes-collection" '
        'aria-labelledby="quotes-heading">'
    ]
    lines.append('  <h2 id="quotes-heading">Complete Quote Collection</h2>')

    for seg_title, seg_id, quotes in collected:
        lines.append('  <div class="quote-group">')
        lines.append(f'    <h3>{esc(seg_title)}</h3>')
        for q in quotes:
            text = esc(q.get("text", ""))
            ts = q.get("timestamp", "")
            context = esc(q.get("context", ""))
            lines.append(
                f'    <blockquote class="insight-quote" '
                f'data-timestamp="{esc(ts, quote=True)}">'
            )
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
            lines.append('    </blockquote>')
        lines.append('  </div>')

    lines.append("</section>")
    return "\n".join(lines)


def build_themes_html_legacy(data: JSON) -> str:
    """Build cross-cutting themes section (legacy)."""
    themes: list[dict[str, Any]] = data.get("themes", [])  # type: ignore[assignment]
    if not themes:
        return ""

    segments: list[dict[str, Any]] = data.get("segments", [])  # type: ignore[assignment]
    seg_title_by_id: dict[str, str] = {}
    for seg in segments:
        seg_title_by_id[seg.get("id", "")] = seg.get("title", "Unknown")

    lines: list[str] = [
        '<section class="supplemental-section cross-themes" '
        'aria-labelledby="themes-heading">'
    ]
    lines.append('  <h2 id="themes-heading">Cross-Cutting Themes</h2>')

    for theme in themes:
        name = esc(theme.get("name", "Untitled Theme"))
        desc = esc(theme.get("description", ""))
        refs: list[str] = theme.get("segment_refs", [])

        lines.append('  <div class="theme-block">')
        lines.append(f'    <h3>{name}</h3>')
        if desc:
            lines.append(f'    <p>{desc}</p>')
        if refs:
            lines.append('    <div class="theme-refs">')
            lines.append('      <span class="theme-ref-label">Appears in:</span>')
            for ref_id in refs:
                seg_title = esc(seg_title_by_id.get(ref_id, ref_id))
                section_id = make_section_id(ref_id)
                lines.append(
                    f'      <a href="#{section_id}" class="topic-tag">{seg_title}</a>'
                )
            lines.append('    </div>')
        lines.append('  </div>')

    lines.append("</section>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core rendering
# ---------------------------------------------------------------------------


def read_template_files(template_dir: str) -> tuple[str, str, str]:
    """Read the three template files from the given directory.

    Args:
        template_dir: Path to assets/report-template/.

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


def render_report(
    data: JSON,
    html_template: str,
    css_content: str,
    js_content: str,
    knowledge_data: JSON | None = None,
) -> str:
    """Produce the final self-contained HTML report.

    Auto-detects the input format:
      - visual_content -> 6 new template variables
      - knowledge       -> 7 legacy template variables (fallback)

    Args:
        data: Parsed JSON dict (visual_content.json or knowledge.json).
        html_template: Raw contents of index.html.
        css_content: Raw contents of style.css.
        js_content: Raw contents of script.js.
        knowledge_data: Optional knowledge.json for predictions in VC mode.

    Returns:
        Complete HTML document as a string.
    """
    fmt = detect_data_format(data)

    # Inline CSS and JS
    combined_css = css_content + "\n" + _SUPPLEMENTAL_CSS
    result = html_template.replace(
        '<link rel="stylesheet" href="style.css">',
        f"<style>\n{combined_css}\n</style>",
    )
    result = result.replace(
        '<script src="script.js"></script>',
        f"<script>\n{js_content}\n</script>",
    )

    # Build replacements based on detected format
    if fmt == "visual_content":
        replacements = _build_visual_content_replacements(data, knowledge_data)
    else:
        # Fall back to legacy knowledge.json rendering
        replacements = _build_legacy_replacements(data)

    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)

    return result


def _build_visual_content_replacements(
    data: JSON,
    knowledge_data: JSON | None = None,
) -> dict[str, str]:
    """Build template variable replacements for visual_content format."""
    # Title and metadata: prefer knowledge.json metadata, fall back to visual_content meta
    title = _build_title_from_data(data, knowledge_data)
    metadata_html = _build_metadata_from_data(data, knowledge_data)

    return {
        "{{TITLE}}": title,
        "{{METADATA_HTML}}": metadata_html,
        "{{HERO_HTML}}": build_hero_html(data),
        "{{THEME_NAV_HTML}}": build_theme_nav_html(data),
        "{{THEME_CONTENT_HTML}}": build_theme_content_html(data),
        "{{TIMELINE_HTML}}": build_timeline_html(data),
        "{{PREDICTIONS_HTML}}": build_predictions_html(data, knowledge_data),
        "{{EVIDENCE_HTML}}": build_evidence_html(data),
    }


def _build_title_from_data(data: JSON, knowledge_data: JSON | None = None) -> str:
    """Build title string from best available metadata source."""
    # Prefer knowledge.json metadata
    if knowledge_data:
        meta: dict[str, Any] = knowledge_data.get("metadata", {})  # type: ignore[assignment]
        if meta.get("title"):
            return esc(meta["title"])
    # Fall back to visual_content meta
    vc_meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    if vc_meta.get("title"):
        return esc(vc_meta["title"])
    return "Interview Report"


def _build_metadata_from_data(data: JSON, knowledge_data: JSON | None = None) -> str:
    """Build metadata HTML from best available metadata source."""
    # Prefer knowledge.json metadata
    src: dict[str, Any] = {}
    if knowledge_data:
        src = knowledge_data.get("metadata", {})  # type: ignore[assignment]

    pieces: list[str] = []

    guest = src.get("guest", {})
    if isinstance(guest, dict) and guest.get("name"):
        name = guest["name"]
        aff = guest.get("affiliation", "")
        if aff:
            pieces.append(f'<span class="meta-guest">{esc(name)}, {esc(aff)}</span>')
        else:
            pieces.append(f'<span class="meta-guest">{esc(name)}</span>')

    interviewer = src.get("interviewer", {})
    if isinstance(interviewer, dict) and interviewer.get("name"):
        pieces.append(f'<span class="meta-host">Host: {esc(interviewer["name"])}</span>')

    if src.get("date"):
        pieces.append(f'<span class="meta-date">{esc(str(src["date"]))}</span>')

    duration = src.get("duration_seconds") or src.get("total_duration_seconds") or 0
    if duration:
        pieces.append(f'<span class="meta-duration">{esc(format_duration(int(duration)))}</span>')

    # Add stats from visual_content meta as fallback
    vc_meta: dict[str, Any] = data.get("meta", {})  # type: ignore[assignment]
    stats = vc_meta.get("stats", {})
    if stats.get("segment_count"):
        pieces.append(f'<span class="meta-stat">{stats["segment_count"]} segments</span>')
    if stats.get("theme_count"):
        pieces.append(f'<span class="meta-stat">{stats["theme_count"]} themes</span>')

    return "\n        ".join(pieces)


def _build_legacy_replacements(data: JSON) -> dict[str, str]:
    """Build template variable replacements for legacy knowledge.json format (7 vars)."""
    return {
        "{{TITLE}}": build_title_legacy(data),
        "{{METADATA_HTML}}": build_metadata_html_legacy(data),
        "{{SIDEBAR_HTML}}": build_sidebar_html_legacy(data),
        "{{CONTENT_HTML}}": build_content_html_legacy(data),
        "{{QUOTES_HTML}}": build_quotes_html_legacy(data),
        "{{PREDICTIONS_HTML}}": build_predictions_html(data),
        "{{THEMES_HTML}}": build_themes_html_legacy(data),
    }


def load_knowledge_json(filepath: str) -> JSON:
    """Load and parse a visual_content.json or knowledge.json file.

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
        raise FileNotFoundError(f"File not found: {filepath}")

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
        raise ValueError(
            f"Expected a JSON object at the root of {filepath}, "
            f"got {type(data).__name__}"
        )

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
        description="Render an interactive HTML interview report from "
        "visual_content.json or knowledge.json.",
    )
    parser.add_argument(
        "json_file",
        metavar="JSON_FILE",
        help="Path to the visual_content.json or knowledge.json input file.",
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
    parser.add_argument(
        "--knowledge",
        "-k",
        metavar="PATH",
        default=None,
        help="Optional path to knowledge.json for predictions fallback "
        "(useful when visual_content.json does not embed predictions).",
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
        script_dir = Path(__file__).resolve().parent
        template_dir = str(script_dir.parent / "assets" / "report-template")

    # Load primary JSON
    try:
        data = load_knowledge_json(args.json_file)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Load optional knowledge.json for predictions fallback
    knowledge_data: JSON | None = None
    if args.knowledge:
        try:
            knowledge_data = load_knowledge_json(args.knowledge)
        except Exception as exc:
            print(f"Warning: Could not load knowledge.json: {exc}", file=sys.stderr)

    # Read template files
    try:
        html_template, css_content, js_content = read_template_files(template_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Render report
    try:
        html = render_report(data, html_template, css_content, js_content, knowledge_data)
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
