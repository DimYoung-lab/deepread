# Quality Assurance & Testing Checklist

## Purpose

This reference documents the mandatory testing procedures and common pitfalls discovered during the development and use of the interview-based-learning skill. Run these checks before considering any output complete.

---

## Pre-Delivery Verification (MANDATORY)

### HTML Report Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Zero JS errors** | Open browser console, load page | No `TypeError`, `ReferenceError`, or other red errors. Favicon 404 is ignorable. |
| 2 | **Collapse/Expand works** | Click "Collapse All" → "Expand All" buttons | All sections close, then all re-open. Chevron rotates on click. |
| 3 | **Search returns results** | Type a known term (e.g., guest name) | Matching text highlighted with `<mark>`, non-matching sections dimmed, result count badge updates |
| 4 | **Search clears cleanly** | Press Escape after search | All highlights removed (>0 `<mark>` elements), no JS errors, all sections visible |
| 5 | **Theme toggle works** | Click theme toggle, reload page | Theme switches light↔dark, preference persists across reload (localStorage) |
| 6 | **Sidebar navigation** | Click each sidebar link | Page scrolls to correct section, URL hash updates to `#seg-seg_XX` |
| 7 | **All 12 segments present** | Count sidebar links or content sections | 12 topic segments in sidebar and main content |
| 8 | **Timestamps are clickable** | Click a timestamp badge | Page scrolls to and briefly highlights the referenced content |
| 9 | **Keyboard shortcuts** | Press `/`, `j`, `k`, `Escape` | `/` focuses search, `j`/`k` navigate sections, `Escape` clears search |

### Mind Map Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Zero JS errors** | Open browser console, load page | No errors |
| 2 | **12 topic nodes visible** | Count topic nodes in legend or visual | 12 topics with labels and "+N" child count badges |
| 3 | **Node expansion works** | Click a topic node | Child insight nodes animate into view, circle count increases |
| 4 | **Expand All works** | Click "Expand All" button | All nodes visible (>700 circles for a full interview) |
| 5 | **Collapse All works** | Click "Collapse All" button | Returns to topic-only view (~26 circles) |
| 6 | **Search filters nodes** | Type a term in search box | Matching nodes remain visible/highlighted, non-matching dim or hide |
| 7 | **Zoom/Pan works** | Mouse wheel scroll, click-drag on canvas | Map zooms in/out smoothly, pans with drag |
| 8 | **Reset View works** | Click "Reset View" button or double-click canvas | Returns to default zoom and centering |
| 9 | **Tooltips on hover** | Hover over a node | Tooltip appears with full text and timestamp |
| 10 | **Title bar complete** | Check top bar | Shows interview title, guest name, date, duration |

### Markdown Report Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **TL;DR has all 6 sections** | grep for section headers | Title+Metadata, Key Takeaways, Surprising Insight, Notable Quotes, Who Should Read, Reading Guide |
| 2 | **TL;DR has 5-7 takeaways** | Count `1. **` through `7. **` | 5-7 numbered bold items |
| 3 | **TL;DR quotes have timestamps** | grep for `>* *XX:XX* ` | Each blockquote has a timestamp in `*HH:MM:SS*` format |
| 4 | **Deep-Dive has all 8 sections** | grep for section headers | Overview, Executive Summary, Topic Deep Dive, Cross-Cutting Themes, Contradictions, Predictions, Quote Collection, Reading Guide |
| 5 | **Deep-Dive references all segments** | grep for segment titles | All 12 Chinese segment titles appear in the deep-dive section |
| 6 | **Quotes are verbatim** | Spot-check 3-5 quotes against knowledge.json | Exact match, no paraphrasing |
| 7 | **Timestamps are in `HH:MM:SS` or `MM:SS`** | Regex scan | No malformed timestamps |
| 8 | **No placeholder text** | grep for "TODO", "FIXME", "placeholder", "TBD" | None found |

---

## Common Pitfalls & Anti-Patterns

### Pitfall 1: `<section>` vs `<details>` Mismatch (CRITICAL)

**Symptom:** Collapse/Expand buttons have no effect. Console shows no errors but sections don't collapse.

**Root Cause:** `generate_html.py` outputs `<section>` elements for topic segments, but the JS collapse/expand functions and CSS styling target `<details>` elements.

**Fix:** Always use `<details open>` + `<summary>` for collapsible topic content. Supplemental sections (quotes collection, predictions table, cross-cutting themes) can remain as `<section>` since they're not collapsible.

**Prevention:** After any change to `generate_html.py`, run Check #2 (Collapse/Expand) from HTML Report Checks above.

### Pitfall 2: DOM Node Reference After Removal (HIGH)

**Symptom:** `TypeError: Cannot read properties of null (reading 'normalize')` when clearing search highlights.

**Root Cause:** In `clearHighlights()`, the code calls `m.parentNode.replaceChild(...)` which removes `m` from the DOM, then immediately calls `m.parentNode.normalize()`. But after `replaceChild`, `m.parentNode` is `null` because `m` is no longer in the DOM tree.

**Fix:** Save the parent node reference BEFORE calling `replaceChild`:

```javascript
// WRONG
m.parentNode.replaceChild(newNode, m);
m.parentNode.normalize();  // BOOM: m.parentNode is null

// RIGHT
var p = m.parentNode;
p.replaceChild(newNode, m);
p.normalize();
```

**Prevention:** Always save parent/sibling references before mutating the DOM.

### Pitfall 3: D3 Data Node Missing `type` Field (HIGH)

**Symptom:** `TypeError: Cannot read properties of undefined (reading 'type')` in `nodeRadius()` or `nodeFill()`.

**Root Cause:** Some D3 hierarchy nodes (especially intermediate nodes created by `d3.hierarchy()`) don't have a `.data` property when first created, or the data transformation doesn't add `type` fields consistently.

**Fix:** Add null guards at the beginning of every D3 accessor function:

```javascript
function nodeRadius(d) {
  if (!d || !d.data) return 5;  // safe fallback
  switch (d.data.type) { ... }
}
```

**Prevention:** ALL D3 accessor functions (`nodeRadius`, `nodeFill`, `nodeLabel`, `nodeOpacity`, etc.) MUST begin with a null guard for `d` and `d.data`. This is a non-negotiable pattern.

### Pitfall 4: CSS `z-index` and `position: sticky` Overlap (MEDIUM)

**Symptom:** Buttons or links in the sidebar cannot be clicked — clicks are intercepted by the sticky header.

**Root Cause:** Both the header (`.site-header`) and sidebar (`.sidebar`) use `position: sticky`. Without explicit `z-index` on the sidebar, and without proper `--header-height` calculation, the sidebar elements overlap with the header area.

**Fix (two-part):**
1. Add `z-index: 50` to `.sidebar` (header has `z-index: 100`, so sidebar stays below)
2. Set `--header-height` dynamically via JS: `document.documentElement.style.setProperty('--header-height', header.offsetHeight + 'px')`
3. Use `--header-height` in sidebar's `top` and `max-height` calculations with a non-zero fallback (e.g., `90px`)

**Prevention:** After any CSS change to header or sidebar, run HTML Report Check #6 (sidebar navigation) and the collapse button test.

### Pitfall 5: Extraction JSON Format Inconsistency (MEDIUM)

**Symptom:** `knowledge.json` merge script reports 0 insights/quotes for some segments.

**Root Cause:** Different extraction sub-agents use different JSON key names for the same data:
- Some use `topics`, `insights`, `golden_quotes` (flat)
- Others use `dimension_1_topics`, `dimension_2_insights` (prefixed)
- Some wrap in nested dicts: `{"dimension_2_insights": {"insights": [...]}}`

**Fix:** The merge script MUST handle all three formats. Use a flexible `get_list()` function that tries multiple key paths and normalizes nested dicts.

**Prevention:** The extraction prompt template in SKILL.md should specify EXACT JSON key names. Add a validation step before extraction that sends a sample output format to sub-agents.

### Pitfall 6: Windows GBK Encoding in Terminal Output (LOW)

**Symptom:** Chinese characters display as garbled text in bash/terminal output.

**Root Cause:** Windows terminals default to GBK code page, but files are UTF-8 encoded.

**Fix:** Always write to files and read them, rather than relying on terminal output. Use `python -c "..."` with output redirection to files when processing Chinese text.

**Prevention:** For any script that outputs Chinese text, provide a `--output` file option.

---

## Regression Test Script

After any change to the skill files, run this sequence:

```bash
# 1. Verify Python scripts compile
python -c "import py_compile; py_compile.compile('scripts/parse_docx.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_html.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_mindmap.py', doraise=True)"

# 2. Parse a known-good transcript
python scripts/parse_docx.py yaoshunyu.docx --output /tmp/test_turns.json

# 3. Verify parse output structure
python -c "
import json
with open('/tmp/test_turns.json') as f: d = json.load(f)
assert d['metadata']['total_turns'] > 900
assert d['metadata']['total_duration_seconds'] > 13000
assert len(d['turns']) > 900
print('Parse: OK')
"

# 4. Generate HTML from known-good knowledge.json
python scripts/generate_html.py output/knowledge.json --output /tmp/test_report.html

# 5. Verify HTML contains key elements
python -c "
with open('/tmp/test_report.html') as f: html = f.read()
assert '<details open' in html, 'Missing <details> elements'
assert '<summary class=\"segment-header\">' in html, 'Missing <summary> elements'
assert 'report-title' in html
assert 'searchInput' in html
print('HTML: OK')
"

# 6. Generate mind map from known-good knowledge.json
python scripts/generate_mindmap.py output/knowledge.json --output /tmp/test_map.html

# 7. Verify mind map contains MINDMAP_DATA
python -c "
import re, json
with open('/tmp/test_map.html') as f: html = f.read()
m = re.search(r'const MINDMAP_DATA = (\{.*?\n\};)', html, re.DOTALL)
assert m, 'MINDMAP_DATA not found'
data = json.loads(m.group(1)[:-1])
assert len(data['topics']) == 12
print('Mind Map: OK')
"

echo "=== All regression tests passed ==="
```
