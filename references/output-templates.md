# Output Templates & Format Specifications

This reference defines the eight canonical output formats produced by the
interview-based-learning pipeline. Every generated artifact must conform to its
template below — use these as the source of truth for structure, content
requirements, and formatting conventions.

**语言规则：** 面向中文母语读者的报告、PDF 和社交媒体输出，新增标题、栏目名、表格标签、解释性文字必须使用中文。只在两类情况下保留英文：一是访谈原话本身包含英文，二是必要术语、平台名、品牌名或行业缩写（如 AI、CEO、L4、VIA、SUV、Token、X/Twitter、LinkedIn）。

---

## 输出格式概览

| # | 格式 | 载体 | 长度目标 | 主要读者 |
|---|--------|--------|---------------|------------------|
| 1 | 速览摘要 | Markdown | 约 500–800 个中文词 | 时间有限、需要快速抓重点的读者 |
| 2 | 深度报告 | Markdown | 覆盖完整访谈 | 研究者、分析师、领域从业者 |
| 3 | 学习卡片 | HTML/CSS/JS | 移动优先卡片组 | 碎片时间学习的专业读者 |
| 4 | 知识图谱 | SVG/Canvas + JS | 交互式可视化 | 偏好结构化探索的读者 |
| 5 | 社交媒体推文 | Markdown | 约 2000–4000 个中文字符 | 社交媒体读者、泛行业读者 |
| 6 | 短播客 | Markdown + MP3 | 按原视频长度自适应，约 3–15 分钟 | 通勤、运动或多任务收听者 |
| 7 | 精美 PDF | PDF（HTML→Playwright） | A4 打印优化 | 离线阅读、转发和归档 |

---

## 1. 速览摘要 (Markdown)

**Purpose:** Distill a 1–3 hour interview into a scannable 5-minute read that
surfaces the highest-signal content. Do not summarize everything — only the
insights that matter.

**Length:** 500–800 words.

### Template Structure

```
# [嘉宾名] × [节目名]：速览

*嘉宾：[姓名]，[身份/机构]｜时长：[X小时Y分钟]｜日期：[YYYY-MM-DD]*

## 核心观点

1. **[一句话加粗核心判断]。** 用 1–2 句说明语境、原因和含义。
2. **[一句话加粗核心判断]。** 用 1–2 句补充解释。
3. ...
   *(5–7 total, numbered)*

## 最令人意外的洞察

[一段，3–5 句。指出最反直觉、最新鲜或最能改变读者判断的洞察，并说明它挑战了哪种常见看法。]

## 值得引用的金句

> "[原文金句]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

> "[Verbatim quote]" — *[HH:MM:SS]*

*(3–5 quotes total. Select only the most memorable, tweetable, or
revealing lines. Timestamps must be exact.)*

## 适合谁读

[1–2 句说明最适合阅读的人群。要具体到角色、领域、资历或正在面对的问题。]

## 阅读指南

[2–4 句说明时间有限时应该优先读哪些章节或主题。引用深度报告章节名时使用中文标题。]
```

### 核心观点规则

- Each takeaway must be a **claim**, not a topic label. Wrong: "Discussion of
  GPU shortages." Correct: "GPU shortages will persist until 2028 because
  advanced packaging capacity is the real bottleneck, not wafer supply."
- Takeaways should be **self-contained** — readable without having heard the
  interview.
- Order by **importance**, not chronological order.
- 避免只复述嘉宾背景或履历的“观点”。

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
# [嘉宾名] × [节目名]：深度报告

*嘉宾：[姓名]，[身份/机构]｜主持：[姓名]｜时长：[X小时Y分钟]｜日期：[YYYY-MM-DD]｜来源：[文件名或链接]*

---

## 访谈概览

### 嘉宾简介
[简洁说明嘉宾当前角色、重要经历或成就，以及为什么他/她有资格讨论本期主题。3–5 句。]

### 访谈背景
[说明这场访谈发生的背景：新书、研究发布、行业事件、长期争论或当前业务节点。1–2 句。]

### 关键数据
| 指标 | 数值 |
|--------|-------|
| 覆盖话题数 | [N] |
| 提取金句数 | [N] |
| 重要预测数 | [N] |
| 对话轮次 | [N] |

---

## 执行摘要

[第 1 段：概括整场访谈的总论点。嘉宾真正想表达的核心故事是什么？]

[第 2 段：串联 3–5 个最重要的支撑洞察，形成连贯叙事，而不是简单列表。]

[第 3 段：说明影响、风险或行动启发。读者理解这场访谈后应该如何调整判断？]

---

## 阅读指南

| 读者类型 | 推荐阅读 | 预计时间 |
|---------------|---------------------|----------------|
| 管理者 / 决策者 | 执行摘要、预测总结 | 5 分钟 |
| 实践者 / 工程师 | 话题深度分析、跨领域主题 | 20 分钟 |
| 研究者 / 分析师 | 完整深度报告 | 45 分钟 |
| 快速了解者 | 速览摘要 | 3 分钟 |

---

## 话题深度分析

### [话题 1 标题] *(HH:MM:SS – HH:MM:SS)*

#### 背景
[1 段：说明该话题为什么重要、它在整场访谈中的位置，以及嘉宾在这里提供了什么判断。]

#### 核心论点

[2–4 段叙事分析。必须覆盖：嘉宾的立场或判断、他/她给出的理由或证据、承认的反例或限制、它和其他话题的关系。]

> **核心引述** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **核心引述** *(HH:MM:SS)*:
> "[Verbatim quote]"

> **数据点：**
> - **[中文标签]**：[数值与来源语境]
> - **[中文标签]**：[数值与来源语境]

---

### [话题 2 标题] *(HH:MM:SS – HH:MM:SS)*

[Same structure as above. Repeat for all topics, typically 6–12.]

---

## 跨领域主题

### [主题名]

[1 段：说明这个主题如何跨越多个话题，并给出来自不同段落的具体例子。]

**跨话题例证:**
- 从 **[话题 A]**：[带时间戳的引述或转述]
- 从 **[话题 B]**：[带时间戳的引述或转述]
- 从 **[话题 C]**：[带时间戳的引述或转述]

---

## 矛盾与未解问题

| # | 张力 / 问题 | 出现场景 | 处理状态 |
|---|-------------------|---------|-------------------|
| 1 | [描述矛盾或未解问题] | [出现位置和时间戳] | 已解决 / 未解决 / 嘉宾暂未展开 |
| 2 | ... | ... | ... |

---

## 预测总结

| # | 预测 | 时间窗口 | 置信度 | 条件 / 限制 |
|---|-----------|--------------|------------|----------------------|
| 1 | [预测内容] | [例如 12–18 个月、到 2027 年] | 高 / 中 / 低 | [什么条件会改变该判断] |
| 2 | ... | ... | ... | ... |

---

## 金句全集

### [话题名]
1. *(HH:MM:SS)* "[原文金句]" — 语境：[1 句中文说明]
2. *(HH:MM:SS)* "[原文金句]" — 语境：[1 句中文说明]

### [话题名]
1. *(HH:MM:SS)* "[原文金句]" — 语境：[1 句中文说明]
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
| **统计数据** | 数字、比例、规模或成本信息 |
| **实体** | 被提到的组织、公司或人物 |
| **基准** | 对比性表现、排名或量级判断 |
| **论文** | 被引用的论文、作者或年份 |
| **事件** | 历史事件、发布时间点或业务节点 |
| **预测** | 对未来时间、趋势或结果的判断 |

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
| 9 | Closing Card | 核心观点总结、阅读指南链接、分享操作 |

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
strong lead, memorable quotes, and clear points.

**Length:** 2000–4000 words.

**File:** `social-[guest-lastname]-[YYYYMMDD].md`

### Template Structure

```markdown
# [有记忆点的中文标题]

*基于：[嘉宾名]在[节目名]中的访谈｜日期：[YYYY-MM-DD]*

## 开场

[1–2 段。用一个强钩子开头：尖锐问题、反直觉判断、关键数字或具体场景。随后说明这场访谈揭示了什么，以及为什么值得继续读。避免“最近我有幸采访了……”这类套话。]

---

## [主题 1：具体、有判断力的小标题]

[2–3 段叙事。按照嘉宾展开观点的方式讲清楚语境、洞察和影响。使用具体细节，不堆抽象词。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 2：小标题]

[2–3 段。每个主题都应像一篇能独立成立的小短文，同时服务于全文主线。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 3：小标题]

[2–3 段。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 4：小标题]

[2–3 段。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 5：小标题]

[2–3 段。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 6：小标题]

[2–3 段。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## [主题 7：小标题]

[2–3 段。]

> "[嘉宾原文金句]" — *[HH:MM:SS]*

---

## 只记住三件事

1. **[一句话洞察]。** 一句中文语境或影响说明。
2. **[一句话洞察]。** 一句中文语境或影响说明。
3. **[一句话洞察]。** 一句中文语境或影响说明。

---

## 适合谁读

[1–2 句。具体说明读者角色、领域、资历或正在面对的问题。]

---

## 继续深入

[链接到深度报告、学习卡片和知识图谱。用 1–2 句邀请读者继续阅读完整分析。]

*完整访谈：[原始访谈或播客链接]*
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
- **“只记住三件事”** 是浓缩部分。这三条必须自洽、有记忆点，并能给读者行动或判断启发。
- All quotes must be verbatim and timestamped.

### Voice

- 语气自然但有判断力，像在给聪明、好奇的同行解释。
- 避免学术腔和营销腔。除“只记住三件事”外，尽量少用项目符号。
- 段落要短，每段最多 3–5 句，适合社交媒体快速扫读。

---

## 6. 短播客脚本 (Markdown + MP3)

**Purpose:** A script optimized for text-to-speech (TTS) synthesis that
distills the interview into a compact, listenable audio piece. Produces the
plain-text script and one final BGM-mixed MP3 audio file.
Designed for consumption during commutes, workouts, or household tasks.

**时长：** 按原始材料长度自适应。默认目标：
`target_minutes = clamp(round(source_minutes * 0.10), 3, 15)`.
Character budget: `target_chars = target_minutes * 320`, with ±12% tolerance.

**Files:**
- Script: `podcast-script-[guest-lastname]-[YYYYMMDD].md`
- Audio: `podcast-[guest-lastname]-[YYYYMMDD].mp3`

### Editorial Workflow

Use `scripts/prepare_podcast_brief.py` to prepare a source brief. The final
podcast script is written by the language model from the brief, then reviewed
before TTS.

```bash
python scripts/prepare_podcast_brief.py output/[dir]/data/knowledge.json --turns output/[dir]/data/turns-corrected.json --visual output/[dir]/data/visual_content.json --output output/[dir]/audio/podcast-brief-[guest]-[YYYYMMDD].md

# Claude writes output/[dir]/audio/podcast-script-[guest]-[YYYYMMDD].md from the brief.

python scripts/review_podcast_script.py output/[dir]/audio/podcast-script-[guest]-[YYYYMMDD].md --knowledge output/[dir]/data/knowledge.json
```

The final script file must contain only spoken text. Do not include metadata
headers, section delimiters, stage directions, fixed labels such as
`HOST:`/`GUEST:`, or character-budget notes inside the script, because TTS
will read them aloud.

### Spoken Structure

1. Fixed strong opening: two short paragraphs, no labels:
   - `今天我们用[目标时长]拆解[嘉宾]在[节目/访谈]里的核心判断。`
   - `这场访谈表面聊[A、B、C]，但真正的主线是：[一句话核心问题/判断]。`
   Then move directly into the first theme.
2. Topic body: explain what the guest believes, why they believe it, and why
   a busy listener should care. Use 3–7 themes only as source material, not
   as a mechanical table of contents.
3. Closing: synthesize what the listener should take away. Point to the full
   report/cards/map for details, but do not make the podcast sound like an
   index to the report.

### Script Writing Rules

- **Model-written, not mechanically stitched.** Use the brief as source
  material, then write natural spoken prose that connects points with clear
  reasoning. Do not concatenate theme bullets, quotes, or canned transitions.
- **Opening must have a hook.** Follow the fixed opening pattern above. Avoid
  flat openings such as "本期播客将总结..." or generic greetings. The listener
  should know the episode's central question within the first 20 seconds.
- **Pure spoken text only.** No markdown, metadata headers, section markers,
  `HOST:`/`GUEST:` labels, code fences, or fixed budget notes in the file.
- **Write for the ear, not the eye.** Use short sentences. Prefer concrete
  nouns and active verbs. Avoid parentheticals, footnotes, and nested
  clauses. Read every line aloud (or mentally) before finalizing.
- **Natural transitions.** Every theme section must begin with a transition
  sentence that connects it to the previous theme. The listener should feel
  guided, not jolted.
- **Quotes must be verbatim** from the transcript when used, but do not speak
  timestamps aloud. The podcast is for understanding the guest's views, not
  locating evidence in the source file.
- **Think from the listener's point of view.** A listener who skips the full
  interview wants the core argument, reasoning, stakes, tensions, and useful
  useful points. Do not read out source-navigation details.
- **Review before TTS.** A reviewer agent/model must reject scripts that sound
  like a report outline, repeat canned phrases, leak internal prompt wording,
  or fail to explain the guest's actual opinions.
- **Closing must synthesize**, not summarize. Don't list all 7 themes again.
  Distill into 3 integrated listener-facing points.
- **Character budget**: calculate from source duration. Use
  `target_minutes = clamp(round(source_minutes * 0.10), 3, 15)` and
  `target_chars = target_minutes * 320`, with ±12% tolerance.

### TTS 制作说明

- 脚本文件是唯一数据源；MP3 是其渲染产物。
- 使用 MiniMax Token Plan（speech-2.8 系列，通过 `mmx-cli`）进行语音合成。
  - 需安装 `npm install -g mmx-cli` 并认证 `mmx auth login --api-key sk-cp-...`。
  - Token Plan Plus：4,000 字符/天，28,000 字符/周。
  - 支持 30+ 中文语音，语速调节（0.5–2.0）。语速用于自然听感，不用于强行凑固定时长。
- 如 mmx CLI 不可用，仅输出 Markdown 脚本文件，并注明：
  "MP3 未生成 — 需要 MiniMax Token Plan（mmx-cli）"
- 合成时直接读取纯口播文本。时长估计和字符预算保留在 CLI 输出和 QA 检查中，不写入脚本正文。
- 生成原声 MP3 后，立即运行 `generate_bgm_podcast.py` 将 BGM 混入同名
  `podcast-[guest]-[YYYYMMDD].mp3`。最终 audio 目录只保留这一个用户可见
  MP3；不要保留原声 MP3、`*-bgm.mp3` 或 `bgm-podcast-*.mp3`。

---

## 7. 精美 PDF (Styled PDF)

**Purpose:** Generate clean, print-optimized PDFs from the Markdown output files. Designed for offline reading, sharing, and archival by Chinese readers.

**File:** `report-[guest-lastname]-[YYYYMMDD].pdf`, `tldr-[guest-lastname]-[YYYYMMDD].pdf`

**Generation:** Run `scripts/generate_pdf.py` with `--type` flag:

```bash
# 深度报告 PDF（含报告头 + 页眉）
python scripts/generate_pdf.py output/[dir]/reports/report-[guest]-[YYYYMMDD].md --type report

# 速览摘要 PDF（紧凑版）
python scripts/generate_pdf.py output/[dir]/reports/tldr-[guest]-[YYYYMMDD].md --type tldr
```

### 设计规格

- **页面尺寸**：A4（210mm × 297mm），可通过 `--page-size` 调整。
- **配色**：米白底色（#fdfbf7）+ 酒红强调色（#722f37），与学习卡片设计系统一致。
- **字体**：中文优化字体栈（Songti SC / PingFang SC），使用固定 `pt` 尺寸。
- **报告头**：深度报告使用紧凑报告头，展示标题、嘉宾、节目、主持、日期和时长，不使用独立空白封面。
- **页眉页脚**：左页显示嘉宾，右页显示报告标题，页脚显示页码。
- **正文页面**：白色页边距 + 米白内容区，避免复杂分割线。
- **表格**：酒红表头 + 浅色隔行底色，减少逐行边框。
- **引用块**：保留细左侧强调线和浅色背景，用于提示原文引用。
- **分页**：深度报告采用自然分页；执行摘要和阅读指南应合并在一页或连续呈现，不产生大面积空白。
- **数据点**：数据点标题和数据列表必须处于同一个 callout 背景块内，避免视觉脱节。
- **TL;DR 密度**：速览 PDF 应控制在 1–2 页，优先通过版式密度、页边距和标题间距优化，而不是删掉关键信息。

### Template Variants

| `--type` | Template | Features |
|----------|----------|----------|
| `report` | `report-wrapper.html.j2` | 紧凑报告头、页眉页码、自然分页、完整章节层级 |
| `tldr` | `tldr-wrapper.html.j2` | 紧凑版式，无封面，不强制章节分页 |

**Requirements:** `markdown-it-py`, `Jinja2`, `playwright` (Chromium).

---

## Cross-Format Consistency Rules

1. **Timestamps**: All timestamps across all eight formats use the same
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

`[YYYYMMDD]` is the interview date when provided or detectable from metadata. If no interview date is available, use today's date as the fallback. The output directory and every generated file must use the same date token; do not derive filenames from the folder creation date.

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
