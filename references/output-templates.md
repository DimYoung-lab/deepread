# Output Templates & Format Specifications

This reference defines the ten canonical output formats produced by the
interview-based-learning pipeline. Every generated artifact must conform to its
template below — use these as the source of truth for structure, content
requirements, and formatting conventions.

---

## 输出格式概览

| # | Format | Medium | Length Target | Primary Audience |
|---|--------|--------|---------------|------------------|
| 1 | 速览摘要 | Markdown | 500–800 words | Time-pressed readers scanning for signal |
| 2 | 深度报告 | Markdown | Comprehensive (full transcript coverage) | Researchers, analysts, domain specialists |
| 3 | 学习卡片 | HTML/CSS/JS | Mobile-first card deck | Busy professionals learning in short bursts |
| 4 | 知识图谱 | SVG/Canvas + JS | Interactive visualization | Visual thinkers, knowledge explorers |
| 5 | 社交媒体推文 | Markdown | 2000–4000 words | Social media followers, general public |
| 6 | 短播客 | Markdown + MP3 | 10–15 min audio | Commuters, multitaskers, auditory learners |
| 7 | 精美 PDF | PDF (via HTML→Playwright) | Print-optimized A4 | Offline readers, report distribution |
| 8 | 访谈封面图 | PNG (MiniMax image-01) | 2:3 editorial cover | Social sharing, report cover |
| 9 | 金句图文卡 | PNG (MiniMax image-01) | 3:4 atmospheric illustrations | Social media (WeChat/Micro-blog) |
| 10 | BGM增强播客 | MP3 (MiniMax music-2.6 + ffmpeg) | Podcast + ambient BGM | Immersive listening |

---

## 1. 速览摘要 (Markdown)

**Purpose:** Distill a 1–3 hour interview into a scannable 5-minute read that
surfaces the highest-signal content. Do not summarize everything — only the
insights that matter.

**Length:** 500–800 words.

### Template Structure

```
# [Guest Name] x [Show Name]: TL;DR

*Guest: [Name], [Affiliation] | Duration: [Xh Ym] | Date: [YYYY-MM-DD]*

## 核心观点

1. **[Bold claim one sentence].** Context or elaboration, 1–2 sentences. Why this matters or what it implies.
2. **[Bold claim one sentence].** Context or elaboration, 1–2 sentences.
3. ...
   *(5–7 total, numbered)*

## 最令人意外的洞察

[One paragraph, 3–5 sentences. Highlight the single most counterintuitive,
novel, or paradigm-shifting revelation. Explain why it challenges
conventional wisdom and what the reader should reconsider.]

## 值得引用的金句

> "[Verbatim quote]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

*(3–5 quotes total. Select only the most memorable, tweetable, or
revealing lines. Timestamps must be exact.)*

## 适合谁读

[1–2 sentences defining the ideal reader. Be specific: role, domain,
seniority level, or problem context. Example: "AI researchers building
production RAG systems who struggle with chunking strategies."]

## 阅读指南

[2–4 sentences prioritizing which sections or topics to read if time
is limited. Guide the reader to the highest-signal content. Reference
specific Deep-Dive Report sections by name when they exist.]
```

### 核心观点规则

- Each takeaway must be a **claim**, not a topic label. Wrong: "Discussion of
  GPU shortages." Correct: "GPU shortages will persist until 2028 because
  advanced packaging capacity is the real bottleneck, not wafer supply."
- Takeaways should be **self-contained** — readable without having heard the
  interview.
- Order by **importance**, not chronological order.
- Avoid takeaways that merely state the guest's background or biography.

### 值得引用的金句规则

- Quotes must be **verbatim** transcript excerpts, not paraphrases.
- Each quote must carry a timestamp in `*HH:MM:SS*` format.
- Prefer quotes that are: surprising, pithy, controversial, or actionable.
- Avoid quotes longer than 3 sentences; trim with `[...]` where needed.
- Do not alter wording — if a quote is slightly unclear, use a different one.

### 最令人意外的洞察规则

- Must be **genuinely unexpected** relative to mainstream discussion of the
  topic, not just a strong opinion.
- If nothing in the interview is truly surprising, select the **most
  underappreciated** insight instead, and frame it as such.
- Include a brief contrast with the conventional view so the reader understands
  why it is surprising.

---

## 2. 深度报告 (Markdown)

**Purpose:** Comprehensive, reference-quality coverage of the entire interview.
A reader should be able to cite this report instead of re-watching the
interview.

**Length:** Comprehensive (typically 3,000–8,000 words depending on interview
length). No hard cap — completeness is the priority.

### 完整章节模板

```markdown
# [Guest Name] on [Show Name]: Full Report

*Guest: [Name], [Affiliation/Title] | Host: [Name] | Duration: [Xh Ym] | Date: [YYYY-MM-DD] | Episode: [# or URL]*

---

## 访谈概览

### 嘉宾简介
[Concise background: current role, notable prior roles, key publications
or achievements, and why they are an authority on the topic. 3–5 sentences.]

### 访谈背景
[What prompted this conversation — book launch, research publication,
industry event, or ongoing debate. 1–2 sentences.]

### 关键数据
| Metric | Value |
|--------|-------|
| Total topics covered | [N] |
| Total quotes extracted | [N] |
| Notable predictions made | [N] |
| Word count | [N] |

---

## 执行摘要

[Paragraph 1: The overarching argument or thesis of the interview. What is
the single most important story the guest is telling?]

[Paragraph 2: The 3–5 most important supporting insights, connected in a
coherent narrative arc. Show how they relate to each other, not just
a list.]

[Paragraph 3: Implications, stakes, or calls to action. What should the
reader do differently after understanding this interview?]

---

## 阅读指南

| Reader Profile | Recommended Sections | Estimated Time |
|---------------|---------------------|----------------|
| Executive / Decision-maker | 执行摘要, 预测总结 | 5 min |
| Practitioner / Engineer | 话题深度分析 (technical topics), 跨领域主题 | 20 min |
| Researcher / Analyst | Full report | 45 min |
| Casual listener | 速览摘要 | 3 min |

---

## 话题深度分析

### [Topic 1 Title] *(HH:MM:SS – HH:MM:SS)*

#### 背景
[1 paragraph: why this topic matters, how it fits into the broader
conversation, and what the guest brings to it.]

#### 核心论点

[2–4 paragraphs of narrative analysis. Cover:
- The guest's position or claim
- The reasoning or evidence they offer
- Counterpoints or nuance they acknowledge
- How this relates to other topics in the interview]

> **核心引述** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **核心引述** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **数据点:**
> - **[Label]**: [Value and source context]
> - **[Label]**: [Value and source context]

---

### [Topic 2 Title] *(HH:MM:SS – HH:MM:SS)*

[Same structure as above. Repeat for all topics, typically 6–12.]

---

## 跨领域主题

### [Theme Name]

[1 paragraph: the pattern observed across multiple topics, with
specific examples from different segments.]

**跨话题例证:**
- From **[Topic A]**: [quote or paraphrase with timestamp]
- From **[Topic B]**: [quote or paraphrase with timestamp]
- From **[Topic C]**: [quote or paraphrase with timestamp]

---

## 矛盾与未解问题

| # | Tension / Question | Context | Resolution Status |
|---|-------------------|---------|-------------------|
| 1 | [Describe the contradiction] | [Where it appears, with timestamps] | Resolved / Unresolved / Guest deferred |
| 2 | ... | ... | ... |

---

## 预测总结

| # | Prediction | Time Horizon | Confidence | Conditions / Caveats |
|---|-----------|--------------|------------|----------------------|
| 1 | [What is predicted] | [e.g., 12–18 months, by 2027] | High / Medium / Low | [What would change the prediction] |
| 2 | ... | ... | ... | ... |

---

## 金句全集

### [Topic Name]
1. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]
2. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]

### [Topic Name]
1. *(HH:MM:SS)* "[Quote text]" — Context: [1-sentence setup]
...

---

### 章节排序规则

- Topics in the 话题深度分析 must appear in **chronological order** as they occur
  in the interview, with segment timestamps.
- 跨领域主题 are sorted by **significance** (most important first).
- Quotes in the 金句全集 are grouped **by topic**, not
  chronologically, so readers can find quotes by subject.
- Predictions are numbered within the table; sort by **time horizon**
  (nearest first).
- **阅读指南** appears early (after 执行摘要) so
  readers can decide how to approach the report before diving in.

### 数据点徽章类型

When inserting a 数据点, classify it:

| Badge | Use When |
|-------|----------|
| **统计数据** | A numerical finding or percentage |
| **实体** | A named organization, company, or person referenced |
| **基准** | A comparative performance or ranking figure |
| **论文** | A cited academic paper with title/author/year |
| **事件** | A referenced historical event or milestone |
| **预测** | A projection or model output |

### 引述格式规则

- All quotes must be **verbatim** from the transcript — never paraphrase
  inside quotation marks.
- Timestamp format: `*(HH:MM:SS)*` after the quote, or `*(HH:MM:SS)*` inline.
- Use `[...]` for omissions; use `[clarification]` only when a pronoun
  or reference is ambiguous without context.
- If a quote exceeds 4 lines, consider breaking it with an ellipsis or
  selecting the most impactful portion.

---

## 3. 学习卡片规格说明

**Purpose:** A mobile-first card deck that presents interview knowledge as a
card-based tap/scroll experience — exactly 9 cards, each building on the last
to form a complete narrative arc. Optimized for busy professionals absorbing
insights in short bursts on a phone.

**File:** `cards-[guest-lastname]-[YYYYMMDD].html`

### Card Deck Structure (9 Cards Total)

| Card | Type | Purpose |
|------|------|---------|
| 1 | Hero Cover | Guest name, show name, date, duration, dominant theme; sets the hook |
| 2 | Theme Card 1 | First cross-cutting theme — the most important insight |
| 3 | Theme Card 2 | Second cross-cutting theme |
| 4 | Theme Card 3 | Third cross-cutting theme |
| 5 | Theme Card 4 | Fourth cross-cutting theme |
| 6 | Theme Card 5 | Fifth cross-cutting theme |
| 7 | Theme Card 6 | Sixth cross-cutting theme |
| 8 | Theme Card 7 | Seventh cross-cutting theme |
| 9 | Closing Card | Key takeaways summary, reading guide links, share actions |

Each Theme Card (2–8) distills one cross-cutting theme from the interview into
a self-contained, card-sized insight. The cards are ordered by significance,
not chronology — the most impactful theme comes first.

### Card Anatomy

Each card follows a fixed upper-half / lower-half layout optimized for
thumb-reachable content on mobile:

```
┌──────────────────────────────┐
│  Badge (theme category)      │  ← top of card, accent pill
│                              │
│  Claim (bold headline)       │  ← 1–2 lines, largest type on card
│                              │
│  Narrative paragraph         │  ← 2–4 sentences, readable prose
│                              │
│  Pull-quote                  │  ← verbatim quote in italic, with timestamp
│                              │
│  ▼ Expand Evidence           │  ← tap to reveal supporting data
│  ┌──────────────────────┐    │
│  │ Data point 1         │    │  ← hidden until expanded
│  │ Data point 2         │    │
│  │ Cross-reference link │    │
│  └──────────────────────┘    │
└──────────────────────────────┘
```

**Badge**: A small pill label indicating theme category (e.g., "Technology",
"Policy", "Economics", "Culture"). Rendered in the theme's accent color.

**Claim**: A single bold sentence — the card's thesis. Large type (min 20px
on mobile), no more than 2 lines on a mobile screen at comfortable reading size.

**Narrative**: 2–4 sentences expanding on the claim. Written for a busy
professional reader — concise, concrete, no jargon without explanation.

**Pull-quote**: One verbatim quote from the transcript that anchors the
claim. Italic, with a left border accent and timestamp in `HH:MM:SS` format.

**Expandable Evidence**: Hidden by default, revealed on tap/click. Contains
supporting data points, statistics, and cross-references to other cards, the
知识图谱, or the full 深度报告.

### Navigation

Navigation is card-based: the user moves through the deck one card at a time.

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
- A visible progress indicator at the bottom of each card shows current
  position (e.g., "3 / 9" with filled/empty dots or numbered pill).
- Keyboard shortcuts are disabled when focus is in an input or textarea.

### Responsive Design

- **Mobile-first (default)**: card fills the viewport (`100vw` x `100dvh`),
  single card visible at a time, large touch targets (minimum 44px).
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

- Transition between cards: a horizontal slide with fade, duration 250–350ms,
  easing `cubic-bezier(0.4, 0, 0.2, 1)`.
- Respect `prefers-reduced-motion: reduce` — disable slide, use instant
  cross-fade instead.

### CSS Architecture

- All styles inline in a `<style>` block. No external dependencies.
- Use CSS custom properties for themeable values, switched via a `data-theme`
  attribute on `<html>`.
- Mobile-first media queries; cards are designed for phone screens first.

---

## 4. 知识图谱规格说明

**Purpose:** An interactive mind-map visualization of the interview's knowledge
structure. The map shows how topics, insights, and evidence connect — enabling
spatial exploration of the content.

**Implementation:** SVG (preferred for accessibility and text rendering) or
HTML5 Canvas. D3.js is acceptable as the sole external dependency if loaded
from CDN.

### Node Hierarchy

The knowledge map is organized as a labeled, hierarchical tree with four levels
and cross-links between leaf nodes:

```
Central Thesis (Level 0):
  └─ The interview's single overarching argument — placed at the center

Themes (Level 1 — 跨领域主题, 5–8 nodes):
  └─ Theme A ─── Theme B ─── Theme C ─── ...
     │              │              │
Arguments (Level 2 — Supporting Arguments, 2–5 per theme):
  └─ Argument A1   └─ Argument B1   └─ Argument C1
     Argument A2      Argument B2      Argument C2
     ...              ...              ...
     │
Evidence (Level 3 — Quotes, Data, Statistics, 2–5 per argument):
  └─ Quote A1a       Data A2a
     Quote A1b       Data A2b
     Statistic A1c   ...
     │
     └── Cross-links (dashed edges) connect related evidence
         across different themes and arguments, forming a network
         layer on top of the tree structure.
```

The hierarchy flows from abstract to concrete: the **central thesis** is the
broadest claim, **themes** break it into major dimensions, **arguments**
support each theme with specific reasoning, and **evidence** anchors every
argument in quotes, data points, or statistics from the transcript.
Cross-links reveal connections between evidence nodes across different
branches of the tree, transforming the pure hierarchy into an interconnected
knowledge graph.

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

## 5. 社交媒体推文 (Markdown)

**Purpose:** A long-form social media post (e.g., LinkedIn article, Substack,
X long-form, or newsletter-ready) that transforms the interview's deepest
insights into a narrative-driven, shareable piece. Written with a hook-driven
structure optimized for social platform reading behavior — short paragraphs,
strong lead, memorable quotes, and clear takeaways.

**Length:** 2000–4000 words.

**File:** `social-[guest-lastname]-[YYYYMMDD].md`

### Template Structure

```markdown
# [Attention-Grabbing Title]

*By [Author Name] | [YYYY-MM-DD] | Based on my conversation with [Guest Name] on [Show Name]*

## Lead

[1–2 paragraphs. Open with a hook — a provocative question, a startling
statistic, a counterintuitive claim, or a vivid scene. Then state what the
conversation revealed and why it matters. The lead must make the reader
want to continue. Avoid generic openings like "Recently I had the pleasure
of speaking with..."]

---

## [Theme 1: Subheading — A compelling, specific statement]

[2–3 paragraphs of narrative. Tell the story of this theme as the guest
unfolded it — context, insight, implication. Use concrete details, not
abstractions. Show the reader why this theme matters in their world.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 2: Subheading]

[2–3 paragraphs. Same structure. Each theme section should feel like a
mini-essay that could stand alone but builds toward the larger argument.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 3: Subheading]

[2–3 paragraphs.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 4: Subheading]

[2–3 paragraphs.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 5: Subheading]

[2–3 paragraphs.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 6: Subheading]

[2–3 paragraphs.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## [Theme 7: Subheading]

[2–3 paragraphs.]

> "[Verbatim quote from guest]" — *[HH:MM:SS]*

---

## If You Only Remember 3 Things

1. **[Single-sentence insight].** One line of context or implication.
2. **[Single-sentence insight].** One line of context or implication.
3. **[Single-sentence insight].** One line of context or implication.

---

## Who This Is For

[1–2 sentences. Define the audience with specificity: role, domain,
seniority, or problem context. Example: "Product leaders navigating the
shift from SaaS to AI-native experiences who need mental models, not
hype."]

---

## Go Deeper

[Link to the full Deep-Dive Report, Learning Cards, and Knowledge Map.
1–2 sentences inviting the reader to explore the complete analysis.]

*Full conversation: [URL to original interview/podcast episode]*
```

### Structure Rules

- **7 theme sections exactly.** Extract the seven most significant themes
  from the interview and present them in order of descending impact (most
  important first, not chronological).
- **Each theme section** must have: a compelling subheading (a claim, not a
  label), 2–3 narrative paragraphs, and at least one verbatim quote with
  timestamp.
- **Lead** must be hook-driven. Do not open with biographical pleasantries
  or an "I sat down with..." cliche. Start with the most arresting insight
  or question.
- **"If You Only Remember 3 Things"** is the distillation section. These
  three takeaways must be self-contained, memorable, and actionable.
- All quotes must be verbatim and timestamped.

### Voice

- Conversational but authoritative. Write as if explaining to a smart,
  curious peer over coffee.
- Avoid academic tone. Avoid marketing hype. Avoid bullet-point lists
  (except the "3 Things" section).
- Use short paragraphs (3–5 sentences max). Social readers scan; dense
  blocks lose them.

---

## 6. 短播客脚本 (Markdown + MP3)

**Purpose:** A script optimized for text-to-speech (TTS) synthesis that
distills the interview into a compact, listenable audio piece. Produces both
the plain-text script and, when TTS tooling is available, an MP3 audio file.
Designed for consumption during commutes, workouts, or household tasks.

**Duration:** 10–15 minutes of audio (approximately 2500–3500 characters of
spoken script at ~250 characters per minute).

**Files:**
- Script: `podcast-script-[guest-lastname]-[YYYYMMDD].md`
- Audio: `podcast-[guest-lastname]-[YYYYMMDD].mp3`

### Template Structure

```
=== SHORT PODCAST SCRIPT ===
Guest: [Full Name]
Show: [Show Name]
Date: [YYYY-MM-DD]
Estimated duration: [10–15] min
Target character count: 2500–3500 characters (spoken text only)
================================

=== OPENING (30 seconds) ===

[1 paragraph, ~125 characters. Hook the listener immediately with the
most compelling idea from the conversation. Identify the guest, the show,
and the central thesis. Avoid "Welcome to..." cliches. Start with the
insight, then attribute it.

Example pattern: "[Guest] believes [surprising claim]. I sat down with
her on [Show] to understand why. Here's what I learned in our
[XX]-minute conversation."]

=== TRANSITION: Opening → Theme 1 ===

[A single sentence, ~50 characters, bridging from the opening to the
first theme. Smooth, spoken-word cadence. Example: "Let's start with
the biggest idea she shared — [theme summary]."]

=== THEME 1: [Subheading — conversational, not academic] (1–2 min) ===

[2 paragraphs, ~300–500 characters. Tell the story of this theme as if
explaining it to a friend. Include the guest's key claim, the reasoning,
and why it matters. Use concrete examples. End with a verbatim quote
from the transcript, introduced naturally.

Intro to quote: "Here's how [guest first name] put it..."
Quote: "[verbatim quote]"

Closing line for this theme: a single sentence that crystallizes the
insight and transitions to the next theme.]

=== TRANSITION: Theme 1 → Theme 2 ===

[A bridging sentence (~50 chars). Pattern: "That connects directly to
something else [guest first name] talked about — [next theme hook]."]

=== THEME 2: [Subheading] (1–2 min) ===

[Same structure as Theme 1. ~300–500 characters.]

=== TRANSITION: Theme 2 → Theme 3 ===

=== THEME 3: [Subheading] (1–2 min) ===

=== TRANSITION: Theme 3 → Theme 4 ===

=== THEME 4: [Subheading] (1–2 min) ===

=== TRANSITION: Theme 4 → Theme 5 ===

=== THEME 5: [Subheading] (1–2 min) ===

=== TRANSITION: Theme 5 → Theme 6 ===

=== THEME 6: [Subheading] (1–2 min) ===

=== TRANSITION: Theme 6 → Theme 7 ===

=== THEME 7: [Subheading] (1–2 min) ===

=== TRANSITION: Theme 7 → Closing ===

[A sentence that signals the summary is coming. Pattern: "So after
[X minutes] with [guest first name], here's what I'm taking away."]

=== CLOSING (1 minute) ===

[1 paragraph, ~250 characters. Synthesize the 3 most important takeaways
into a cohesive closing statement. No new ideas — only synthesis. End
with a call to action: where to find the full report, learning cards,
and original interview.

Final line pattern: "For the full deep-dive, learning cards, and
knowledge map, visit [link]. The original conversation with [guest
name] is at [URL]."]

=== END OF SCRIPT ===

Character count: [XXXX]
Estimated duration: [XX] min ([XXXX] / 250 chars-per-min)
```

### Script Writing Rules

- **Plain text only.** No markdown in the spoken sections (stage directions
  and section markers use `===` delimiters). The script is fed directly to
  a TTS engine; formatting artifacts would be read aloud.
- **Write for the ear, not the eye.** Use short sentences. Prefer concrete
  nouns and active verbs. Avoid parentheticals, footnotes, and nested
  clauses. Read every line aloud (or mentally) before finalizing.
- **Natural transitions.** Every theme section must begin with a transition
  sentence that connects it to the previous theme. The listener should feel
  guided, not jolted.
- **Quotes must be verbatim** from the transcript. Introduce them naturally
  so the shift to the guest's voice is clear in TTS ("Here's how she put
  it..." or "In his words...").
- **Closing must synthesize**, not summarize. Don't list all 7 themes again.
  Distill into 3 integrated takeaways.
- **Character budget**: aim for 2500–3500 characters of spoken text. At
  ~250 characters per minute, this yields 10–14 minutes of audio. Stay
  within budget — longer scripts produce audio over the 15-minute target.

### TTS 制作说明

- 脚本文件是唯一数据源；MP3 是其渲染产物。
- 使用 MiniMax Token Plan（speech-2.8 系列，通过 `mmx-cli`）进行语音合成。
  - 需安装 `npm install -g mmx-cli` 并认证 `mmx auth login --api-key sk-cp-...`。
  - Token Plan Plus：4,000 字符/天，28,000 字符/周。
  - 支持 30+ 中文语音，语速调节（0.5–2.0）。
- 如 mmx CLI 不可用，仅输出 Markdown 脚本文件，并注明：
  "MP3 未生成 — 需要 MiniMax Token Plan（mmx-cli）"
- 合成前去除所有 `===` 分隔符、转场标记和舞台指示，
  仅将口播文本（含引述的自然引入语）送入 TTS 引擎。

---

## 7. 精美 PDF (Styled PDF)

**Purpose:** Generate professionally styled, print-optimized PDFs from the Markdown output files. Designed for offline reading, sharing, and archival.

**File:** `report-[guest-lastname]-[YYYYMMDD].pdf`, `tldr-[guest-lastname]-[YYYYMMDD].pdf`, `social-[guest-lastname]-[YYYYMMDD].pdf`

**Generation:** Run `scripts/generate_pdf.py` with `--type` flag:

```bash
# 深度报告 PDF（含封面 + 页眉）
python scripts/generate_pdf.py output/[dir]/reports/report-[guest]-[YYYYMMDD].md --type report

# 速览摘要 PDF（紧凑版）
python scripts/generate_pdf.py output/[dir]/reports/tldr-[guest]-[YYYYMMDD].md --type tldr

# 社交媒体 PDF（叙事版）
python scripts/generate_pdf.py output/[dir]/reports/social-[guest]-[YYYYMMDD].md --type social
```

### Design Specification

- **Page size**: A4 (210mm × 297mm), configurable via `--page-size`
- **Color scheme**: Cream (#fdfbf7) + burgundy (#722f37), matching the Learning Cards design system
- **Typography**: Chinese-optimized font stacks (Songti SC / PingFang SC), fixed `pt` sizes
- **Cover page** (report type only): Full-bleed hero layout with guest name, show, host, date, duration
- **Running headers**: Guest name on left pages, report title on right pages
- **Body pages**: White margins with cream content area, page numbers in footer
- **Tables**: Burgundy header row, alternating cream/white row stripes
- **Blockquotes**: 3px burgundy left border, cream background
- **Page breaks**: New page for each h2 section; keep h3/h4 with content; avoid splitting blockquotes and tables

### Template Variants

| `--type` | Template | Features |
|----------|----------|----------|
| `report` | `report-wrapper.html.j2` | Cover page, running headers, full section hierarchy |
| `tldr` | `tldr-wrapper.html.j2` | Compact layout, larger type, no cover |
| `social` | `social-wrapper.html.j2` | Narrative layout, narrower content column |

**Requirements:** `markdown-it-py`, `Jinja2`, `playwright` (Chromium).

---

## 8. 访谈封面图 (Cover Image)

**Purpose:** AI-generated editorial magazine cover that visually represents the interview's core theme. Used as report cover art and social media sharing hero image.

**File:** `cover-[guest-lastname]-[YYYYMMDD].png`

**Generation:**
```bash
python scripts/generate_cover.py output/[dir]/data/knowledge.json
```

**Design spec:**
- Aspect ratio: 2:3 (portrait magazine cover)
- Style: Minimalist editorial, cream + burgundy palette, negative space for text overlay
- Prompt auto-constructed from `knowledge.json` core thesis + cross-cutting themes
- Uses `--prompt-optimizer` for better prompt quality
- Model: MiniMax `image-01`, 1 image per interview

**Integration with other outputs:**
- PDF deep report: Use as optional cover page background (via `--cover-image` flag in `generate_pdf.py`)
- Social media post (Output 5): Include as header image when publishing
- Learning Cards (Output 3): Reference as hero card background

---

## 9. 金句图文卡 (Quote Cards)

**Purpose:** Artistic atmospheric illustrations paired with the interview's top golden quotes. Designed for social media sharing (WeChat Moments, Weibo, Xiaohongshu).

**File:** `quote-NN-[guest-lastname]-[YYYYMMDD].png` (NN = 01, 02, ...)

**Generation:**
```bash
python scripts/generate_quotecards.py output/[dir]/data/knowledge.json --count 4
```

**Design spec:**
- Aspect ratio: 3:4 (portrait, social-media-optimized)
- Style: Atmospheric, soft lighting, poetic mood, warm tones
- Prompt inspired by the quote's sentiment (first 120 chars)
- Ample space for text overlay (quotes to be added in post-processing)
- Model: MiniMax `image-01`, 3-5 images per interview
- 3-second cooldown between requests to respect TPM limits

**Integration with other outputs:**
- Social media post (Output 5): Quote card images complement the post text
- Learning Cards (Output 3): Each theme card can reference its quote illustration
- PDF deep report: Can be embedded as visual breaks between topic sections

---

## 10. BGM增强播客 (BGM-Enhanced Podcast)

**Purpose:** Podcast voiceover mixed with ambient instrumental background music, creating a more immersive listening experience for commuters and multitaskers.

**Files:**
- `podcast-[guest-lastname]-[YYYYMMDD]-bgm.mp3` (mixed version)
- `bgm-podcast-[guest-lastname]-[YYYYMMDD].mp3` (instrumental only)

**Generation:**
```bash
python scripts/generate_bgm_podcast.py output/[dir]/audio/podcast-[guest]-[YYYYMMDD].mp3 --knowledge output/[dir]/data/knowledge.json
```

**Design spec:**
- BGM: Instrumental only, warm + contemplative mood, ~80 BPM
- Mixing: BGM at 30% volume (-10 dB), looped to match voiceover length
- Output: 192 kbps MP3, mono-compatible
- Model: MiniMax `music-2.6`, 1 track per interview

**Integration with other outputs:**
- Podcast (Output 6): Direct enhancement — the BGM version replaces/augments the raw voiceover
- Learning Cards (Output 3): Closing card can link to BGM version for "immersive mode"
- Knowledge Map (Output 4): Optional background ambience toggle

---

## Cross-Format Consistency Rules

1. **Timestamps**: All timestamps across all ten formats use the same
   `HH:MM:SS` or `[HH:MM:SS]` format. No variation.
2. **Guest naming**: Use the guest's full name on first mention in every
   format, then last name only. Consistent across all outputs.
3. **Topic naming**: Topic titles must be identical across the 深度报告, 学习卡片, 知识图谱, 社交媒体推文, and Podcast
   Script.
4. **Quote attribution**: Every quote in every format must include a
   timestamp. Quotes must be verbatim — if a quote appears in multiple
   formats, it must be identical in each.
5. **Color-coding**: When the same topic appears in the 知识图谱 and
   the HTML report (e.g., as section accent colors), use the same hue.

---

## File Naming Convention

| Format | Filename Pattern |
|--------|-----------------|
| 速览摘要 | `tldr-[guest-lastname]-[YYYYMMDD].md` |
| 深度报告 | `report-[guest-lastname]-[YYYYMMDD].md` |
| 学习卡片 | `cards-[guest-lastname]-[YYYYMMDD].html` |
| 知识图谱 | `map-[guest-lastname]-[YYYYMMDD].html` |
| 社交媒体推文 | `social-[guest-lastname]-[YYYYMMDD].md` |
| 短播客脚本 | `podcast-script-[guest-lastname]-[YYYYMMDD].md` |
| 短播客音频 | `podcast-[guest-lastname]-[YYYYMMDD].mp3` |
| 深度报告 PDF | `report-[guest-lastname]-[YYYYMMDD].pdf` |
| 速览摘要 PDF | `tldr-[guest-lastname]-[YYYYMMDD].pdf` |
| 社交媒体 PDF | `social-[guest-lastname]-[YYYYMMDD].pdf` |
