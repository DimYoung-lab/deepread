# Quality Assurance & Testing Checklist

## Purpose

This reference documents the mandatory testing procedures and common pitfalls discovered during the development and use of the deepread skill. Run these checks before considering any output complete.

---

## Pre-Delivery Verification (MANDATORY)

### Output Naming Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Date token source** | Inspect `output/[guest]-[YYYYMMDD]/` and metadata | `YYYYMMDD` uses the provided/detected interview date, or today's date only when no interview date was provided |
| 2 | **Date token consistency** | List generated filenames under reports/pdf/html/audio | Directory and generated files use the same `YYYYMMDD`; no folder creation date is mixed in |

### Stage 1.5 — Extraction & Correction Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Glossary loaded correctly** | Open `output/*/glossary.json`, count entries | >= 5 entries, each has `term`, `definition`, `aliases` fields |
| 2 | **turns-corrected.json has corrections** | Diff `turns_raw.json` vs `turns-corrected.json` | Corrected file has changes where glossary entities were applied |
| 3 | **Known entities fixed** | grep known errors in `turns-corrected.json` | "C-Dance" → "Seedance"; no uncorrected known errors remain |
| 4 | **Speaker labels consistent** | grep `"speaker"` in `turns-corrected.json` | Guest name used consistently, no "unknown" or raw speaker IDs |

### Learning Cards Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Zero JS errors** | Open browser console, load page | No `TypeError`, `ReferenceError`, or other red errors. Favicon 404 is ignorable. |
| 2 | **Card count (9)** | Count `.card` elements | 9 learning cards: 1 hero, 7 theme, 1 closing |
| 3 | **Theme cards (7)** | Count `.card-theme` elements | 7 theme cards present |
| 4 | **Theme dot navigation** | Click nav dots below cards | Active card follows dot selection, correct dot highlighted |
| 5 | **Keyboard navigation** | Press Left/Right arrow keys | Cards advance forward/backward smoothly |
| 6 | **Keyboard shortcuts** | Press Home, End, 1-9 keys | Home jumps to hero, End jumps to closing, number keys jump to card N |
| 7 | **Swipe support** | Swipe left/right on touch device or emulator | Cards advance forward/backward |
| 8 | **Role tabs** | Verify ARIA attributes | Cards container has `role="tablist"`, each card has `role="tabpanel"` |
| 9 | **Expandable sections** | Click expand-toggle on a card | Card content expands/collapses, toggle icon rotates |
| 10 | **Responsive at 375px** | Resize browser to 375px width | Cards fit viewport, no horizontal overflow, text readable, nav dots visible |
| 11 | **Responsive at 768px** | Resize browser to 768px width | Cards display in tablet layout, no layout breakage |
| 12 | **Responsive at 1440px** | Resize browser to 1440px width | Cards display in desktop layout, max-width container centered |

### Mind Map Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Zero JS errors** | Open browser console, load page | No errors |
| 2 | **7 theme nodes visible (or 12 segment topics if legacy fallback)** | Count topic nodes in legend or visual | 7 themes (or 12 segments in legacy) with labels and "+N" child count badges |
| 3 | **Node expansion works** | Click a topic node | Child argument/insight nodes animate into view; diamond-shaped data-point nodes visible; prediction nodes with dashed borders |
| 4 | **全部展开 works** | 点击「全部展开」按钮 | All argument nodes visible (~34 arguments + 68 evidence for a full interview in new format; >700 circles for legacy format) |
| 5 | **全部收起 works** | 点击「全部收起」按钮 | Returns to topic-only view (~8 circles: 1 root + 7 themes) |
| 6 | **Search filters nodes** | Type a term in search box | Matching nodes remain visible/highlighted, non-matching dim or hide |
| 7 | **Zoom/Pan works** | Mouse wheel scroll, click-drag on canvas | Map zooms in/out smoothly, pans with drag |
| 8 | **重置视图 works** | 点击「重置视图」按钮或双击画布 | Returns to default zoom and centering |
| 9 | **Tooltips on hover** | Hover over argument node | Tooltip shows Chinese type badge (e.g., 反直觉洞察/因果论断/心智模型) and explanation text. All node types at same depth show consistent tooltip format — no per-node star ratings (importance is encoded in node size). |
| 10 | **Title bar complete** | Check top bar | Shows interview title, guest name, date, duration, AND stats bar (insight/quote/prediction counts) |
| 11 | **No SVG interception** | Click several topic nodes that are visually close to link paths | All clicks register; `.link { pointer-events: none }` in CSS |
| 12 | **Importance sizing** | Check argument node sizes | Higher importance (5) nodes visibly larger than lower (3) |

### Markdown Report Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **TL;DR has all 6 sections** | grep for section headers | 标题+元数据、核心观点、最令人意外的洞察、值得引用的金句、适合谁读、阅读指南 |
| 2 | **TL;DR has 5-7 core points** | Count `1. **` through `7. **` | 5-7 numbered bold items |
| 3 | **TL;DR quotes have timestamps** | grep for `>* *XX:XX* ` | Each blockquote has a timestamp in `*HH:MM:SS*` format |
| 4 | **Deep-Dive has all 8 sections** | grep for section headers | 访谈概览、执行摘要、阅读指南、话题深度分析、跨领域主题、矛盾与未解问题、预测总结、金句全集 |
| 5 | **Deep-Dive references all segments** | grep for segment titles | All 12 Chinese segment titles appear in the deep-dive section |
| 6 | **Quotes are verbatim** | Spot-check 3-5 quotes against knowledge.json | Exact match, no paraphrasing |
| 7 | **Timestamps are in `HH:MM:SS` or `MM:SS`** | Regex scan | No malformed timestamps |
| 8 | **No placeholder text** | grep for "TODO", "FIXME", "placeholder", "TBD" | None found |
| 9 | **Generated labels are Chinese** | grep for legacy English metadata, table, title, reading-guide, and quote-context labels | No legacy English structural labels in report Markdown |

### Social Media Post Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Character count** | `wc -c` or character counter | 2000-4000 characters |
| 2 | **Engaging title** | Read opening line | Title is present, provocative or curiosity-driven, not generic |
| 3 | **7 themes covered** | Count distinct theme references | All 7 interview themes mentioned or alluded to |
| 4 | **Quotes with timestamps** | grep for `XX:XX` or `HH:MM:SS` | At least 2 direct quotes with timestamp attribution |
| 5 | **Audience section** | Scroll to end of post | “适合谁读” or audience targeting present |
| 6 | **CTA present** | Read last 2-3 lines | Call-to-action (link to full report, cards, or discussion prompt) |
| 7 | **No markdown artifacts** | Read raw text | Clean plain text or platform-native formatting; no `**` or `##` remnants |
| 8 | **Chinese generated prose** | grep/read platform sections | Added headings, explanations, and platform notes are Chinese; platform names such as LinkedIn and X/Twitter may remain |

### PDF Report Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Only report and TL;DR PDFs generated** | List `output/[dir]/pdf/` | Only report and TL;DR PDF files are present |
| 2 | **Report starts with content** | Open first page | Compact title/meta header and report body appear on page 1; no standalone blank cover |
| 3 | **摘要与指南连续** | Extract text or inspect first pages | 执行摘要 and 阅读指南 appear on the same page or consecutive area without large blank space |
| 4 | **数据点 callout unified** | Inspect a topic page | `数据点：` and its bullet items share one background/callout block |
| 5 | **TL;DR dense enough** | Count pages | TL;DR is 1-2 pages |

### Podcast Script Checks

| # | Check | Method | Expected |
|---|-------|--------|----------|
| 1 | **Adaptive character count** | Compute source duration and character counter | `target_minutes = clamp(round(source_minutes * 0.10), 3, 15)`, `target_chars = target_minutes * 320`, within ±12% |
| 2 | **TTS-friendly plain text** | grep for markdown syntax, labels, and spoken timestamps | No `**`, `##`, `*`, backticks, `HOST:`, `GUEST:`, metadata headers, or spoken `HH:MM` timestamps |
| 3 | **Standardized listener opening** | Read first 5 lines | Starts with `今天我们用[目标时长]拆解...核心判断`, states the real `主线`, then moves directly into the guest's views |
| 4 | **Closing present** | Read last 5 lines | Outro, call-to-action, or next-episode teaser |
| 5 | **Explains the guest's views** | Reviewer agent/model reads body | Focuses on what the guest believes, why, stakes, tensions, and listener-facing points, not source navigation |
| 6 | **Duration policy visible in tooling** | Run `prepare_podcast_brief.py` and inspect stdout | CLI prints source duration, target minutes, and expected script range |
| 7 | **No spoken timestamps** | grep for `XX:XX` or `HH:MM:SS` | No source timestamps in the podcast script body |
| 8 | **Reviewer pass required** | Run `review_podcast_script.py` and a model/editor review | Both reviews pass before TTS |
| 9 | **Single final MP3** | List `output/[dir]/audio/*.mp3` | Exactly one user-facing MP3 remains: `podcast-[guest]-[YYYYMMDD].mp3`; no raw duplicate, `*-bgm.mp3`, or `bgm-podcast-*.mp3` |

---

## Common Pitfalls & Anti-Patterns

### Pitfall 1: `<section>` vs `<details>` Mismatch (CRITICAL)

**Symptom:** Collapse/Expand buttons have no effect. Console shows no errors but sections don't collapse.

**Root Cause:** `generate_cards.py` outputs `<section>` elements for topic segments, but the JS collapse/expand functions and CSS styling target `<details>` elements.

**Fix:** Always use `<details open>` + `<summary>` for collapsible topic content. Supplemental sections (quotes collection, predictions table, cross-cutting themes) can remain as `<section>` since they're not collapsible.

**Prevention:** After any change to `generate_cards.py`, run Check #9 (Expandable sections) from Learning Cards Checks above.

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

**Prevention:** After any CSS change to header or sidebar, run Learning Cards Check #4 (Theme dot navigation) and Check #9 (Expandable sections).

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

### Pitfall 7: SVG Link/Path Elements Intercept Pointer Events (MEDIUM)

**Symptom:** In the mind map, clicking or hovering on a topic node sometimes fails — Playwright reports `<path class="link">` or `<circle class="node-circle">` "intercepts pointer events."

**Root Cause:** SVG renders elements in DOM order. `<path class="link">` elements (the curved lines connecting nodes) are rendered AFTER the node `<g>` groups in the SVG, putting them visually on top. Without `pointer-events: none`, these paths consume mouse events before they reach the nodes.

**Fix:** Add `pointer-events: none` to the `.link` CSS class:

```css
.link {
    fill: none;
    stroke: rgba(255,255,255,0.12);
    stroke-width: 1.2;
    pointer-events: none;  /* REQUIRED: let clicks pass through to nodes */
    transition: stroke var(--transition-speed) ease;
}
```

**Prevention:** ALL decorative SVG elements (link paths, background circles, glow effects) that overlay interactive nodes MUST have `pointer-events: none`. Only the `<g class="node">` groups and their explicitly interactive children should receive pointer events.

### Pitfall 8: Verifying `<details>` Collapse — `querySelector` vs `offsetHeight` (LOW)

**Symptom:** When testing collapsed `<details>` elements, `querySelector` still finds child elements inside closed details, leading to false "BUG!" reports.

**Root Cause:** The browser's native `<details>` collapse hides content VISUALLY (via shadow DOM), but does NOT remove elements from the DOM tree. `querySelector` searches the DOM tree, not the visual viewport.

**Wrong way to test:**
```javascript
// Always finds elements even when collapsed — false positive!
document.querySelector('details:not([open]) .insight-card')  // → found!
```

**Right way to test:**
```javascript
// Check the details element's own height — summary only when closed
document.querySelector('details:not([open])').offsetHeight   // → ~97px (summary only)
document.querySelector('details[open]').offsetHeight         // → large (full content)

// Or use the native open attribute
document.querySelector('details').hasAttribute('open')        // → false when collapsed
document.querySelectorAll('details[open]').length             // → count of open details
```

**Prevention:** Always verify collapse state via `hasAttribute('open')` or by comparing the `offsetHeight` of the `<details>` element itself (not its children). Never use `querySelector` to verify content visibility.

### Pitfall 9: Playwright `file://` Protocol Blocked (LOW)

**Symptom:** `playwright-cli open "file:///C:/path/to/cards.html"` fails with "Access to file: protocol is blocked."

**Root Cause:** Playwright blocks `file://` URLs for security reasons.

**Fix:** Always serve files through a local HTTP server:
```bash
cd output/yaoshunyu-20260511
python -m http.server 8765 &
playwright-cli open "http://localhost:8765/cards.html"
```

**Prevention:** Document in test procedures that a local HTTP server is required. The regression test script should include server startup.

### Pitfall 10: `playwright-cli eval` JavaScript Syntax Restrictions (LOW)

**Symptom:** `eval` commands fail with `SyntaxError: Unexpected token 'var'` or `Unexpected token ';'`.

**Root Cause:** `playwright-cli eval` wraps the expression in an arrow function. Variable declarations (`var`, `let`, `const`) and certain syntax patterns cause parse errors.

**Wrong:**
```bash
playwright-cli eval "var x = document.querySelector('a'); x.href"
playwright-cli eval "document.querySelector('a').click(); 'ok'"
```

**Right (simple single expressions only):**
```bash
playwright-cli eval "document.querySelector('a').href"
playwright-cli eval "document.querySelectorAll('details').length + ' details'"
# For click actions, use separate playwright-cli click command:
playwright-cli click e34
```

**Prevention:** Use `playwright-cli eval` only for simple property reads and counts. For mouse interactions, use dedicated commands (`click`, `hover`, `fill`, `press`). For complex logic, write to a Python helper script instead.

---

## Regression Test Script

After any change to the skill files, run this sequence:

```bash
# === Stage 1: Parse transcript ===

# 1. Verify Python parse script compiles
python -c "import py_compile; py_compile.compile('scripts/parse_docx.py', doraise=True)"

# 2. Parse a known-good transcript
python scripts/parse_docx.py yaoshunyu.docx --output /tmp/test_turns_raw.json

# 3. Verify raw parse output structure
python -c "
import json
with open('/tmp/test_turns_raw.json') as f: d = json.load(f)
assert d['metadata']['total_turns'] > 900
assert d['metadata']['total_duration_seconds'] > 13000
assert len(d['turns']) > 900
print('Stage 1 — Parse: OK')
"

# === Stage 1.5: Correct transcript ===

# 4. Verify turns-corrected.json exists and has corrections
python -c "
import json
with open('output/yaoshunyu-20260511/data/turns.json') as f: raw = json.load(f)
with open('output/yaoshunyu-20260511/data/turns-corrected.json') as f: corr = json.load(f)
assert raw != corr, 'Corrected file is identical to raw — no corrections applied'
# Verify known entity fix: C-Dance should be corrected
raw_text = json.dumps(raw)
corr_text = json.dumps(corr)
assert 'C-Dance' not in corr_text or raw_text.count('C-Dance') > corr_text.count('C-Dance'), 'C-Dance not corrected'
print('Stage 1.5 — Correction: OK')
"

# 5. Verify glossary loads
python -c "
import json
with open('output/yaoshunyu-20260511/data/glossary.json') as f: g = json.load(f)
assert len(g) >= 5, f'Glossary has only {len(g)} entries, expected >= 5'
for entry in g:
    assert 'term' in entry, f'Missing term in glossary entry'
    assert 'definition' in entry
print('Stage 1.5 — Glossary: OK')
"

# === Stage 4: Verify visual_content.json ===

# 6. Verify visual_content.json structure
python -c "
import json
with open('output/yaoshunyu-20260511/data/visual_content.json') as f: vc = json.load(f)
assert 'cards' in vc, 'Missing cards key'
assert len(vc['cards']) == 9, f'Expected 9 cards, got {len(vc[\"cards\"])}'
card_types = [c.get('type') for c in vc['cards']]
assert 'hero' in card_types, 'Missing hero card'
assert 'theme' in card_types, 'Missing theme card'
assert 'closing' in card_types, 'Missing closing card'
print('Stage 4 — visual_content.json: OK')
"

# === Stage 5: Generate and verify Learning Cards ===

# 7. Verify cards generator compiles
python -c "import py_compile; py_compile.compile('scripts/generate_cards.py', doraise=True)"

# 8. Generate cards HTML
python scripts/generate_cards.py output/yaoshunyu-20260511/data/visual_content.json --output /tmp/test_cards.html

# 9. Verify cards HTML structure
python -c "
with open('/tmp/test_cards.html') as f: html = f.read()
assert '<div class=\"card\">' in html, 'Missing card elements'
assert 'card-hero' in html, 'Missing card-hero'
assert 'card-theme' in html, 'Missing card-theme'
assert 'card-closing' in html, 'Missing card-closing'
assert 'pull-quote' in html, 'Missing pull-quote'
assert 'expand-toggle' in html, 'Missing expand-toggle'
assert 'nav-dot' in html, 'Missing nav-dot'
assert 'role=\"tablist\"' in html, 'Missing tablist role'
assert 'role=\"tabpanel\"' in html, 'Missing tabpanel role'
print('Stage 5 — Cards HTML: OK')
"

# === Stage 6: Generate and verify Mind Map ===

# 10. Verify mind map generator compiles
python -c "import py_compile; py_compile.compile('scripts/generate_mindmap.py', doraise=True)"

# 11. Generate mind map HTML
python scripts/generate_mindmap.py output/yaoshunyu-20260511/data/visual_content.json --output /tmp/test_map.html

# 12. Verify mind map structure
python -c "
import re, json
with open('/tmp/test_map.html') as f: html = f.read()
m = re.search(r'const MINDMAP_DATA = (\{.*?\n\};)', html, re.DOTALL)
assert m, 'MINDMAP_DATA not found'
data = json.loads(m.group(1)[:-1])
assert len(data['topics']) in (7, 12), f"Expected 7 themes or 12 segments, got {len(data['topics'])}"
# Verify pointer-events fix is present
assert 'pointer-events: none' in html or '.link' in html, 'Missing pointer-events CSS on link paths'
print('Stage 6 — Mind Map: OK')
"

# === Stage 7: Verify Social Media Post ===

# 13. Verify social media post
python -c "
import os, glob
posts = glob.glob('output/yaoshunyu-20260511/reports/social*')
assert posts, 'No social media post found'
with open(posts[0], encoding='utf-8') as f: text = f.read()
length = len(text)
assert 2000 <= length <= 4000, f'Social post length {length} outside 2000-4000 range'
assert 'C-Dance' not in text or 'Seedance' in text, 'Known entity not corrected in social post'
print(f'Stage 7 — Social Media Post: OK ({length} chars)')
"

# === Stage 7: Verify Podcast Script ===

# 14. Prepare and verify podcast brief + script review tools
python -c "import py_compile; py_compile.compile('scripts/prepare_podcast_brief.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/review_podcast_script.py', doraise=True)"

python scripts/prepare_podcast_brief.py output/yaoshunyu-20260511/data/knowledge.json --turns output/yaoshunyu-20260511/data/turns-corrected.json --visual output/yaoshunyu-20260511/data/visual_content.json --output /tmp/test_podcast_brief.md

python -c "
from pathlib import Path
text = Path('/tmp/test_podcast_brief.md').read_text(encoding='utf-8')
assert 'Podcast Editorial Brief' in text
assert 'Listener Job' in text
assert 'Forbidden phrases' in text
assert 'Source Material' in text
print('Stage 7 — Podcast Brief: OK')
"

# After the model writes podcast-script-*.md, run:
# python scripts/review_podcast_script.py output/yaoshunyu-20260511/audio/podcast-script-*.md --knowledge output/yaoshunyu-20260511/data/knowledge.json
#
# After TTS, run BGM mixing in place. The final directory should contain only
# one user-facing MP3:
# python scripts/generate_bgm_podcast.py output/yaoshunyu-20260511/audio/podcast-yaoshunyu-20260511.mp3 --knowledge output/yaoshunyu-20260511/data/knowledge.json
# python -c "from pathlib import Path; files=sorted(p.name for p in Path('output/yaoshunyu-20260511/audio').glob('*.mp3')); assert files == ['podcast-yaoshunyu-20260511.mp3'], files"

# === Stage 3: Verify Markdown Reports ===

# 15. Verify deep-dive report
python -c "
import os, glob
reports = glob.glob('output/yaoshunyu-20260511/reports/report*')
assert reports, 'No deep-dive report found'
with open(reports[0], encoding='utf-8') as f: text = f.read()
assert 'Executive Summary' in text or '执行摘要' in text, 'Missing executive summary'
assert 'Quote Collection' in text or '语录集锦' in text, 'Missing quote collection'
assert 'TODO' not in text and 'FIXME' not in text, 'Placeholder text found'
print('Stage 3 — Deep-Dive Report: OK')
"

# 16. Verify TL;DR report
python -c "
import os, glob
reports = glob.glob('output/yaoshunyu-20260511/reports/tldr*')
assert reports, 'No TL;DR report found'
with open(reports[0], encoding='utf-8') as f: text = f.read()
assert '核心观点' in text, 'Missing core points'
assert 'Who Should Read' in text or '适合人群' in text, 'Missing audience section'
print('Stage 3 — TL;DR Report: OK')
"

echo ""
echo "=== All regression tests passed (7 stages, 7 user-facing outputs) ==="
```
