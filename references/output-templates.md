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
| 3 | Learning Cards | HTML/CSS/JS | Mobile-first card deck | Busy professionals learning in short bursts |
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

## 3. Learning Cards Specification

**Purpose:** A mobile-first card deck that presents interview knowledge as a
swipeable, tap-through experience — 9 cards total, each building on the last
to form a complete narrative arc. Optimized for busy professionals absorbing
insights in short bursts.

**File:** `cards-[guest-lastname]-[YYYYMMDD].html`

### Card Deck Structure (9 Cards Total)

| Card | Type | Purpose |
|------|------|---------|
| 1 | Hero Cover | Guest name, show name, date, duration, dominant theme |
| 2 | Theme Card 1 | First cross-cutting theme from the interview |
| 3 | Theme Card 2 | Second cross-cutting theme |
| 4 | Theme Card 3 | Third cross-cutting theme |
| 5 | Theme Card 4 | Fourth cross-cutting theme |
| 6 | Theme Card 5 | Fifth cross-cutting theme |
| 7 | Theme Card 6 | Sixth cross-cutting theme |
| 8 | Theme Card 7 | Seventh cross-cutting theme |
| 9 | Closing Card | Key takeaways summary, reading guide links, share actions |

### Card Anatomy

Each card follows a fixed upper-half / lower-half layout:

```
┌──────────────────────────┐
│  Badge (theme category)  │  ← top of card
│                          │
│  Claim (bold headline)   │  ← 1–2 lines, large type
│                          │
│  Narrative paragraph     │  ← 2–4 sentences, readable prose
│                          │
│  Pull-quote              │  ← verbatim quote in italic, with timestamp
│                          │
│  ▼ Expand Evidence      │  ← toggle to reveal supporting data
│  ┌──────────────────┐    │
│  │ Data point 1     │    │  ← hidden until expanded
│  │ Data point 2     │    │
│  │ Cross-reference  │    │
│  └──────────────────┘    │
└──────────────────────────┘
```

**Badge**: A small pill label indicating theme category (e.g., "Technology",
"Policy", "Economics", "Culture"). Rendered in the theme's accent color.

**Claim**: A single bold sentence — the card's thesis. Large type, no more
than 2 lines on a mobile screen at comfortable reading size.

**Narrative**: 2–4 sentences expanding on the claim. Written for a busy
professional reader — concise, concrete, no jargon without explanation.

**Pull-quote**: One verbatim quote from the transcript that anchors the
claim. Italic, with a left border accent and timestamp in `HH:MM:SS` format.

**Expandable Evidence**: Hidden by default, revealed on tap/click. Contains
supporting data points, statistics, and cross-references to other cards or
the full Deep-Dive Report.

### Navigation

| Method | Behavior |
|--------|----------|
| Swipe left/right (touch) | Advance to next card / return to previous card |
| Arrow Left / Arrow Right | Same as swipe |
| Keys `1`–`9` | Jump directly to card by number |
| `j` / `k` | Next card / previous card (vim-style) |
| `Space` | Advance to next card |
| `Home` / `End` | Jump to first card / last card |
| `Escape` | Collapse any expanded evidence panel |

- Navigation wraps: from card 9, advancing goes to card 1 (and vice versa).
- A progress indicator (dots or a numbered pill, e.g. "3 / 9") is visible
  at the bottom of each card.
- Shortcuts are disabled when focus is in an input or textarea.

### Responsive Design

- **Mobile-first**: card fills the viewport (100vw x 100dvh), single card
  visible at a time, large touch targets (minimum 44px).
- **Tablet (768px+)**: card max-width 600px, centered with generous padding,
  evidence panel may remain open as a side panel.
- **Desktop (1024px+)**: card max-width 720px, evidence panel slides in
  from the right or expands inline with smooth animation.

### Theme Support

- **Dark mode** and **Light mode** themes.
- Default: respect `prefers-color-scheme`. Fallback to light.
- Toggle button with sun/moon icon in the card footer or a fixed corner.
- Persist preference to `localStorage` under key `card-theme-preference`.

**Light palette:**
- Card background: `#ffffff`
- Text: `#1a1a2e`
- Accent: `#2563eb`
- Quote border: `#94a3b8`
- Evidence panel background: `#f8f9fa`

**Dark palette:**
- Card background: `#0f172a`
- Text: `#e2e8f0`
- Accent: `#60a5fa`
- Quote border: `#475569`
- Evidence panel background: `#1e293b`

### Card Transition Animation

- Transition between cards: a subtle slide (horizontal translate) with fade,
  duration 250–350ms, easing `cubic-bezier(0.4, 0, 0.2, 1)`.
- Respect `prefers-reduced-motion: reduce` — disable slide, use instant
  cross-fade instead.

### CSS Architecture

- All styles inline in a `<style>` block. No external dependencies.
- Use CSS custom properties for themeable values, switched via a `data-theme`
  attribute on `<html>`.
- Mobile-first media queries.

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
  └─ Central Thesis — the interview's single overarching argument
     │
Level 1 (Ring 1 — Cross-Cutting Themes, 5–8 nodes):
  └─ Theme A ─── Theme B ─── Theme C ─── ...
     │              │              │
Level 2 (Ring 2 — Supporting Arguments, 2–5 per theme):
  └─ Argument A1   └─ Argument B1   └─ Argument C1
     Argument A2      Argument B2      Argument C2
     ...              ...              ...
     │
Level 3 (Ring 3 — Evidence, 2–5 per argument, plus cross-links):
  └─ Quote A1a       Data A2a
     Quote A1b       Data A2b
     Statistic A1c   ...
     │
     └── Cross-links (dashed edges) connect related evidence
         across different themes and arguments
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
| Learning Cards | `cards-[guest-lastname]-[YYYYMMDD].html` |
| Knowledge Map | `map-[guest-lastname]-[YYYYMMDD].html` |
