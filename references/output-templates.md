# Output Templates & Format Specifications

This reference defines the four canonical output formats produced by the
interview-based-learning pipeline. Every generated artifact must conform to its
template below — use these as the source of truth for structure, content
requirements, and formatting conventions.

---

## Format Overview

| # | Format | Medium | Length Target | Primary Audience |
|---|--------|--------|---------------|------------------|
| 1 | TL;DR Quick Summary | Markdown | 500–800 words | Time-pressed readers scanning for signal |
| 2 | Deep-Dive Report | Markdown | Comprehensive (full transcript coverage) | Researchers, analysts, domain specialists |
| 3 | Interactive HTML Report | HTML/CSS/JS | Self-contained single file | Engaged readers who navigate non-linearly |
| 4 | Knowledge Map | SVG/Canvas + JS | Interactive visualization | Visual thinkers, knowledge explorers |

---

## 1. TL;DR Quick Summary (Markdown)

**Purpose:** Distill a 1–3 hour interview into a scannable 5-minute read that
surfaces the highest-signal content. Do not summarize everything — only the
insights that matter.

**Length:** 500–800 words.

### Template Structure

```
# [Guest Name] x [Show Name]: TL;DR

*Guest: [Name], [Affiliation] | Duration: [Xh Ym] | Date: [YYYY-MM-DD]*

## 核心观点 (Key Takeaways)

1. **[Bold claim one sentence].** Context or elaboration, 1–2 sentences. Why this matters or what it implies.
2. **[Bold claim one sentence].** Context or elaboration, 1–2 sentences.
3. ...
   *(5–7 total, numbered)*

## 最令人意外的洞察 (Most Surprising Insight)

[One paragraph, 3–5 sentences. Highlight the single most counterintuitive,
novel, or paradigm-shifting revelation. Explain why it challenges
conventional wisdom and what the reader should reconsider.]

## 值得引用的金句 (Notable Quotes)

> "[Verbatim quote]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

*(3–5 quotes total. Select only the most memorable, tweetable, or
revealing lines. Timestamps must be exact.)*

## 适合谁读 (Who Should Read This)

[1–2 sentences defining the ideal reader. Be specific: role, domain,
seniority level, or problem context. Example: "AI researchers building
production RAG systems who struggle with chunking strategies."]

## 阅读建议 (Reading Guide)

[2–4 sentences prioritizing which sections or topics to read if time
is limited. Guide the reader to the highest-signal content. Reference
specific Deep-Dive Report sections by name when they exist.]
```

### Rules for Key Takeaways

- Each takeaway must be a **claim**, not a topic label. Wrong: "Discussion of
  GPU shortages." Correct: "GPU shortages will persist until 2028 because
  advanced packaging capacity is the real bottleneck, not wafer supply."
- Takeaways should be **self-contained** — readable without having heard the
  interview.
- Order by **importance**, not chronological order.
- Avoid takeaways that merely state the guest's background or biography.

### Rules for Notable Quotes

- Quotes must be **verbatim** transcript excerpts, not paraphrases.
- Each quote must carry a timestamp in `*HH:MM:SS*` format.
- Prefer quotes that are: surprising, pithy, controversial, or actionable.
- Avoid quotes longer than 3 sentences; trim with `[...]` where needed.
- Do not alter wording — if a quote is slightly unclear, use a different one.

### Rules for Most Surprising Insight

- Must be **genuinely unexpected** relative to mainstream discussion of the
  topic, not just a strong opinion.
- If nothing in the interview is truly surprising, select the **most
  underappreciated** insight instead, and frame it as such.
- Include a brief contrast with the conventional view so the reader understands
  why it is surprising.

---

## 2. Deep-Dive Report (Markdown)

**Purpose:** Comprehensive, reference-quality coverage of the entire interview.
A reader should be able to cite this report instead of re-watching the
interview.

**Length:** Comprehensive (typically 3,000–8,000 words depending on interview
length). No hard cap — completeness is the priority.

### Full Section Template

```markdown
# [Guest Name] on [Show Name]: Full Report

*Guest: [Name], [Affiliation/Title] | Host: [Name] | Duration: [Xh Ym] | Date: [YYYY-MM-DD] | Episode: [# or URL]*

---

## 访谈概览 (Interview Overview)

### Guest Bio (1 paragraph)
[Concise background: current role, notable prior roles, key publications
or achievements, and why they are an authority on the topic. 3–5 sentences.]

### Interview Context
[What prompted this conversation — book launch, research publication,
industry event, or ongoing debate. 1–2 sentences.]

### Key Stats
| Metric | Value |
|--------|-------|
| Total topics covered | [N] |
| Total quotes extracted | [N] |
| Notable predictions made | [N] |
| Word count | [N] |

---

## 执行摘要 (Executive Summary)

[Paragraph 1: The overarching argument or thesis of the interview. What is
the single most important story the guest is telling?]

[Paragraph 2: The 3–5 most important supporting insights, connected in a
coherent narrative arc. Show how they relate to each other, not just
a list.]

[Paragraph 3: Implications, stakes, or calls to action. What should the
reader do differently after understanding this interview?]

---

## 话题深度分析 (Topic-by-Topic Deep Dive)

### [Topic 1 Title] *(HH:MM:SS – HH:MM:SS)*

#### 背景 (Context)
[1 paragraph: why this topic matters, how it fits into the broader
conversation, and what the guest brings to it.]

#### 核心论点 (Key Arguments)

[2–4 paragraphs of narrative analysis. Cover:
- The guest's position or claim
- The reasoning or evidence they offer
- Counterpoints or nuance they acknowledge
- How this relates to other topics in the interview]

> **Key Quote** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **Key Quote** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **Data Point Callout:**
> - **[Label]**: [Value and source context]
> - **[Label]**: [Value and source context]

---

### [Topic 2 Title] *(HH:MM:SS – HH:MM:SS)*

[Same structure as above. Repeat for all topics, typically 6–12.]

---

## 跨领域主题 (Cross-Cutting Themes)

### [Theme Name]

[1 paragraph: the pattern observed across multiple topics, with
specific examples from different segments.]

**Examples across topics:**
- From **[Topic A]**: [quote or paraphrase with timestamp]
- From **[Topic B]**: [quote or paraphrase with timestamp]
- From **[Topic C]**: [quote or paraphrase with timestamp]

---

## 矛盾与未解问题 (Contradictions & Open Questions)

| # | Tension / Question | Context | Resolution Status |
|---|-------------------|---------|-------------------|
| 1 | [Describe the contradiction] | [Where it appears, with timestamps] | Resolved / Unresolved / Guest deferred |
| 2 | ... | ... | ... |

---

## 预测总结 (Predictions Summary)

| # | Prediction | Time Horizon | Confidence | Conditions / Caveats |
|---|-----------|--------------|------------|----------------------|
| 1 | [What is predicted] | [e.g., 12–18 months, by 2027] | High / Medium / Low | [What would change the prediction] |
| 2 | ... | ... | ... | ... |

---

## 金句全集 (Complete Quote Collection)

### [Topic Name]
1. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]
2. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]

### [Topic Name]
1. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]
...

---

## 阅读指南 (Reading Guide)

| Reader Profile | Recommended Sections | Estimated Time |
|---------------|---------------------|----------------|
| Executive / Decision-maker | Executive Summary, Predictions Summary | 5 min |
| Practitioner / Engineer | Topic Deep Dive (technical topics), Cross-Cutting Themes | 20 min |
| Researcher / Analyst | Full report | 45 min |
| Casual listener | TL;DR Quick Summary | 3 min |
```

### Section Ordering Rules

- Topics in the Deep Dive must appear in **chronological order** as they occur
  in the interview, with segment timestamps.
- Cross-Cutting Themes are sorted by **significance** (most important first).
- Quotes in the Complete Quote Collection are grouped **by topic**, not
  chronologically, so readers can find quotes by subject.
- Predictions are numbered within the table; sort by **time horizon**
  (nearest first).

### Data Point Callout Badge Types

When inserting a data point callout, classify it:

| Badge | Use When |
|-------|----------|
| **statistic** | A numerical finding or percentage |
| **entity** | A named organization, company, or person referenced |
| **benchmark** | A comparative performance or ranking figure |
| **paper** | A cited academic paper with title/author/year |
| **event** | A referenced historical event or milestone |
| **forecast** | A projection or model output |

### Quote Formatting Rules

- All quotes must be **verbatim** from the transcript — never paraphrase
  inside quotation marks.
- Timestamp format: `*(HH:MM:SS)*` after the quote, or `*(HH:MM:SS)*` inline.
- Use `[...]` for omissions; use `[clarification]` only when a pronoun
  or reference is ambiguous without context.
- If a quote exceeds 4 lines, consider breaking it with an ellipsis or
  selecting the most impactful portion.

---

## 3. Interactive HTML Report Specification

**Purpose:** A self-contained, single-file HTML page that wraps the Deep-Dive
Report content with navigation, search, theming, and interaction affordances.
No build step, no external dependencies (all CSS/JS inline).

**File:** `interview-report.html` — fully standalone, openable directly in a
browser.

### Required Features

#### 3.1 Layout & Navigation

- **Fixed left sidebar** (280px wide, `position: sticky` on desktop) containing:
  - Report title (linked — scrolls to top)
  - Section navigation links (generated from `<h2>` and `<h3>` headings)
  - Scroll-spy active state: highlight the nav item corresponding to the
    currently visible section using `IntersectionObserver`
  - Search input field at the top of the sidebar
- **Main content area**: fluid width, max-width 800px, centered with padding.
- **Responsive breakpoint at 768px**: sidebar collapses to a horizontal
  top navigation bar. On mobile, the sidebar is hidden by default with a
  hamburger toggle.

#### 3.2 Section Collapse

- All topic sections (chapters of the Deep Dive) are wrapped in
  `<details>` / `<summary>` elements.
- Sections are **open by default** on desktop, **collapsed by default**
  on mobile.
- "Expand All" and "Collapse All" buttons at the top of the content area
  (hidden when all sections are already in the target state).

#### 3.3 Search

- **Search-as-you-type**: results update on every keystroke (debounced
  150ms).
- Search scope: all text content in the main content area.
- **Real-time highlighting**: matching text is wrapped in `<mark>` elements
  with a yellow background (`#ff0` in light mode, `#b8860b` in dark mode).
- **Result count** displayed in the sidebar: "N matches" / "No matches".
- Press `Escape` to clear the search and remove highlights.
- Press `/` to focus the search input.

#### 3.4 Timestamp Badges

- Styling: monospace font (`Consolas`, `Menlo`, or `monospace`),
  pill-shaped (`border-radius: 999px`), inline-block.
- Appearance: subtle background tone, small padding (2px 8px), font-size
  0.85em.
- Behavior: clicking a timestamp badge scrolls the page to the
  corresponding quote or section and briefly highlights the target element
  with a CSS animation (pulse or flash background, 1.5s duration).

#### 3.5 Theme Toggle

- Two themes: **Light** and **Dark**.
- Default: respect `prefers-color-scheme` media query. If no preference,
  default to light.
- Toggle button in the sidebar (sun/moon icon via CSS or Unicode).
- Persist user choice to `localStorage` under key `theme-preference` with
  values `"light"` or `"dark"`.
- On page load, check localStorage first, then fall back to system
  preference.

**Light theme palette:**
- Background: `#ffffff`
- Text: `#1a1a2e`
- Sidebar background: `#f8f9fa`
- Accent: `#2563eb`
- Quote border: `#94a3b8`
- Code / timestamp background: `#e2e8f0`

**Dark theme palette:**
- Background: `#0f172a`
- Text: `#e2e8f0`
- Sidebar background: `#1e293b`
- Accent: `#60a5fa`
- Quote border: `#475569`
- Code / timestamp background: `#334155`

#### 3.6 Reading Progress Bar

- Thin bar (3–4px height) fixed to the top of the viewport, spanning the
  full width.
- Width percentage = `scrollY / (documentHeight - viewportHeight)`.
- Color: accent color from the active theme.
- `z-index: 1000` to stay above all content.

#### 3.7 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search input |
| `j` | Scroll to next topic section |
| `k` | Scroll to previous topic section |
| `Escape` | Clear search and blur input |
| `o` | Toggle expand/collapse all sections |
| `t` | Toggle theme |

- Shortcuts are disabled when focus is in an input or textarea.
- Display a small toast or notification on first shortcut use to confirm.

#### 3.8 Quote Block Styling

- Quotes rendered as `<blockquote>` elements styled with:
  - Left border (4px, accent-adjacent color)
  - Slightly indented (margin-left: 1.5rem)
  - Italic text
  - Optional: subtle background tint (2–3% opacity)
  - Timestamp badge positioned top-right or inline after the quote text

#### 3.9 Data Point Cards

- Each data point rendered as a `<div class="datapoint-card">` with:
  - A visual type badge (one of: statistic, entity, benchmark, paper, event,
    forecast)
  - The data value in bold or emphasized text
  - Source context in smaller text below
  - Subtle border and background to distinguish from prose

#### 3.10 Print Stylesheet

- `@media print` rules:
  - Hide sidebar, progress bar, search controls, theme toggle,
    expand/collapse buttons
  - Remove background colors (print on white)
  - Use black text, serif font
  - Expand all collapsed sections before print
  - Remove shadows and border-radius
  - Ensure page breaks avoid splitting sections

### CSS Architecture

- Use CSS custom properties for all themeable values and switch them via a
  `data-theme` attribute on `<html>`.
- No CSS framework dependency. All styles handwritten or generated from
  specification.
- Mobile-first media queries: base styles for mobile, then `@media (min-width:
  768px)` for desktop layout.

---

## 4. Knowledge Map Specification

**Purpose:** An interactive mind-map visualization of the interview's knowledge
structure. The map shows how topics, insights, and evidence connect — enabling
spatial exploration of the content.

**Implementation:** SVG (preferred for accessibility and text rendering) or
HTML5 Canvas. D3.js is acceptable as the sole external dependency if loaded
from CDN.

### Node Hierarchy

```
Level 0 (Central Node):
  └─ Interview Title + Guest Name
     │
Level 1 (Ring 1 — Topic Segments, 8–12 nodes):
  └─ Topic A ─── Topic B ─── Topic C ─── ...
     │              │              │
Level 2 (Ring 2 — Key Insights, 3–8 per topic):
  └─ Insight A1   └─ Insight B1   └─ Insight C1
     Insight A2      Insight B2      Insight C2
     Insight A3      Insight B3      ...
     ...             ...
     │
Level 3 (Leaf Nodes — Quotes & Data Points):
  └─ Quote A1a     DataPoint A2a
     Quote A1b     DataPoint A2b
     DataPoint A1c ...
```

### Visual Design

#### Central Node
- Largest node (radius or size ~2x of topic nodes).
- Text: interview title on line 1, guest name on line 2 (smaller font).
- Color: neutral, distinct from topic colors (e.g., dark gray or brand
  color).

#### Topic Nodes (Ring 1)
- Color-coded: each topic gets a distinct hue from a palette of 8–12
  colors, evenly distributed around the HSL wheel.
- Node size is **proportional to the number of insights** in that topic
  (more insights = larger node).
- Label: topic title, truncated to 25 characters with ellipsis.

#### Insight Nodes (Ring 2)
- Smaller than topic nodes, color is a lighter tint of the parent topic's
  color.
- Label: insight summary, truncated to 40 characters.

#### Leaf Nodes (Ring 3)
- Smallest nodes, represented as dots or mini-badges.
- Two visual types:
  - **Quote nodes**: circle with a quotation-mark icon (or `"` character)
  - **Data point nodes**: diamond shape or square with a `#` character
- Color matches parent topic at reduced opacity.

#### Edges / Links
- Curved paths (quadratic Bezier or cubic Bezier) connecting parent to
  child nodes.
- **Edge width** represents insight density or connection strength:
  - Thin (1px): standard connection
  - Medium (2px): moderate density
  - Thick (3px): high density (5+ insights)
- Edge color: a muted version of the parent topic color.

### Layout Algorithm

- **Radial tidy tree**: center node at origin, topic nodes arranged in a
  circle (uniform angular distribution), insight nodes orbit their
  respective topic nodes, leaf nodes at the outermost ring.
- **Spacing**: radial distance between rings proportional to the maximum
  node count at each level.
- **Responsive**: SVG viewBox adapts to window size; minimum viewBox
  of 800x800.

### Interaction Behaviors

#### Click
- Clicking a collapsed topic node **expands** it, revealing its insight
  and leaf children (animated: nodes fade in and slide outward over 300ms).
- Clicking an expanded topic node **collapses** it, hiding children.
- Clicking a leaf node opens a tooltip with full text and timestamp.

#### Hover
- Hovering any node shows a **tooltip** containing:
  - Full text (for truncated labels)
  - Timestamp (if applicable)
  - Topic category
  - Related insights count
- Tooltip appears adjacent to the cursor, offset by 12px.

#### Zoom & Pan
- **Zoom**: mouse wheel or pinch gesture. Scale range: 0.3x to 3x.
- **Pan**: click-and-drag on empty canvas area.
- **Reset view**: double-click empty area or press `0` to reset to default
  zoom and center.
- **Smooth zoom**: use D3 zoom behavior or manual matrix transforms with
  `transition: transform 200ms ease`.

#### Drag
- Nodes are NOT draggable (layout is computed, not force-directed).
- Exception: the user may drag the central node slightly to reposition the
  entire map, but this resets on zoom-to-fit.

### Color Palette Specification

Generate topic colors by dividing the HSL hue wheel (0–360) into N equal
parts, where N is the number of topics (clamped to 8–12). Use:
- Saturation: 65–75%
- Lightness: 55–65% for topic nodes, 75–85% for insight nodes, 85–92% for
  leaf nodes

### Accessibility

- All nodes have `<title>` elements (SVG) or `aria-label` attributes
  (Canvas) with full text content.
- Keyboard navigation: Tab to cycle through nodes, Enter to expand/collapse,
  Arrow keys to move between sibling nodes.
- High-contrast mode: detect `prefers-contrast: more` and boost saturation
  and line widths.
- Reduced motion: when `prefers-reduced-motion: reduce` is set, disable
  expand/collapse animations.

### Export

- Provide a "Download as PNG" button that captures the current SVG/Canvas
  state at 2x resolution.
- Provide a "Download as SVG" button (if SVG-based) that saves the
  current DOM as a standalone `.svg` file.

---

## Cross-Format Consistency Rules

1. **Timestamps**: All timestamps across all four formats use the same
   `HH:MM:SS` or `[HH:MM:SS]` format. No variation.
2. **Guest naming**: Use the guest's full name on first mention in every
   format, then last name only. Consistent across all outputs.
3. **Topic naming**: Topic titles must be identical across the Deep-Dive
   Report, HTML sidebar links, and Knowledge Map topic nodes.
4. **Quote attribution**: Every quote in every format must include a
   timestamp. Quotes must be verbatim — if a quote appears in multiple
   formats, it must be identical in each.
5. **Color-coding**: When the same topic appears in the Knowledge Map and
   the HTML report (e.g., as section accent colors), use the same hue.

---

## File Naming Convention

| Format | Filename Pattern |
|--------|-----------------|
| TL;DR | `tldr-[guest-lastname]-[YYYYMMDD].md` |
| Deep-Dive | `report-[guest-lastname]-[YYYYMMDD].md` |
| Interactive HTML | `report-[guest-lastname]-[YYYYMMDD].html` |
| Knowledge Map | `map-[guest-lastname]-[YYYYMMDD].html` |
