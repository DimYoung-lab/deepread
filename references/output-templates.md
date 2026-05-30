# Output Templates & Format Specifications

This reference defines the six canonical output formats produced by the
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
| 5 | Social Media Post | Markdown | 2000–4000 words | Social media followers, general public |
| 6 | Short Podcast | Markdown + MP3 | 10–15 min audio | Commuters, multitaskers, auditory learners |

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
Knowledge Map, or the full Deep-Dive Report.

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

## 4. Knowledge Map Specification

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

Themes (Level 1 — Cross-Cutting Themes, 5–8 nodes):
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

## 5. Social Media Post (Markdown)

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

## 6. Short Podcast Script (Markdown + MP3)

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

### TTS Production Notes

- The script file is the source of truth; the MP3 is a render of it.
- If TTS tooling is not available in the current environment, produce only
  the Markdown script file. Include a note at the top: "MP3 not generated
  — TTS tooling unavailable in this environment."
- When TTS is available, use a high-quality neural voice. Preferred voice
  characteristics: warm, conversational, clear. Avoid robotic or overly
  formal voices.
- Before rendering, strip all `===` delimiters, transition markers, and
  stage directions. Only the spoken text (including the natural quote
  introductions) goes to the TTS engine.

---

## Cross-Format Consistency Rules

1. **Timestamps**: All timestamps across all six formats use the same
   `HH:MM:SS` or `[HH:MM:SS]` format. No variation.
2. **Guest naming**: Use the guest's full name on first mention in every
   format, then last name only. Consistent across all outputs.
3. **Topic naming**: Topic titles must be identical across the Deep-Dive
   Report, Learning Cards, Knowledge Map, Social Media Post, and Podcast
   Script.
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
| Social Media Post | `social-[guest-lastname]-[YYYYMMDD].md` |
| Short Podcast Script | `podcast-script-[guest-lastname]-[YYYYMMDD].md` |
| Short Podcast Audio | `podcast-[guest-lastname]-[YYYYMMDD].mp3` |
