---
name: interview-based-learning
description: Extract structured knowledge from long interview/podcast transcripts (.docx, .txt, .md) into digestible formats — deep-dive reports, interactive HTML, knowledge maps, and quick summaries. Use when the user wants to distill a recorded conversation, extract insights from an interview transcript, create a knowledge map from a podcast, generate a readable summary of a long dialogue, or turn a talk transcript into a structured learning resource. Trigger words include: 访谈, 播客, 笔录, 逐字稿, 知识提取, 知识图谱, interview transcript, podcast transcript, knowledge extraction.
---

# Interview-Based Learning

Transform long interview transcripts into structured, digestible knowledge. This skill processes 1–3 hour interview recordings (provided as `.docx`, `.txt`, or `.md` transcripts) through a five-stage pipeline: Parse → Segment → Extract → Synthesize → Present.

Place transcript files in the `transcripts/` directory before processing.

## Pipeline Overview

```
Transcript file (.docx / .txt / .md)
        │
        ▼
[Stage 1: Parse]    → turns.json           (scripts/parse_docx.py)
[Stage 2: Segment]  → segments.json         (Claude + segmentation-guide.md)
[Stage 3: Extract]  → segment_N_extraction.json  (parallel sub-agents)
[Stage 4: Synthesize] → knowledge.json       (Claude merge + cross-cutting)
[Stage 5: Present]  → 4 output formats      (Claude + scripts/generate_*.py)
```

Each stage produces a well-defined intermediate artifact. This decouples the pipeline so stages can be re-run independently and output formats can be generated in parallel.

## Stage 1: Parse the Transcript

**Goal:** Convert the raw transcript file into structured JSON with metadata and turns.

### For .docx files

Run the parse script:

```bash
python scripts/parse_docx.py <transcript.docx> --output turns.json
```

The script auto-detects speaker roles (guest vs interviewer by turn count), normalizes timestamps (MM:SS / HH:MM:SS → seconds), and extracts metadata.

### For .txt / .md files

Parse manually using this pattern:

- Identify speaker labels (e.g., `发言人1`, `Speaker A`, `Q:`, `Interviewer:`)
- Extract timestamps with regex: `(\d{1,2}:)?\d{1,2}:\d{2}`
- Build the same JSON structure as the script output

### Expected Output (`turns.json`)

```json
{
  "metadata": {
    "title": "...",
    "date": "YYYY-MM-DD",
    "guest": { "name": "...", "affiliation": "..." },
    "interviewer": { "name": "..." },
    "total_duration_seconds": 13620,
    "total_turns": 967,
    "language": "zh"
  },
  "turns": [
    {
      "index": 1,
      "speaker": "guest",
      "speaker_label": "发言人2",
      "timestamp_raw": "00:08",
      "timestamp_seconds": 8,
      "text": "..."
    }
  ]
}
```

## Stage 2: Segment into Topics

**Goal:** Split the long transcript into 5–12 logical topical segments for focused analysis.

### Process

1. Read `turns.json` — review the full conversation arc
2. Apply the four heuristics from [references/segmentation-guide.md](references/segmentation-guide.md):
   - Natural topic transitions (explicit pivots)
   - Question pivots (interviewer changes question category)
   - Timestamp gaps (unusually long pauses)
   - Keyword clusters (new vocabulary appears)
3. Identify the interview's structural pattern (Classic Arc / Thematic Tour / Conversational Flow)
4. Mark boundaries, adjust for size constraints (~2,000–8,000 chars per segment)
5. Name each segment and assign time ranges

### Output

Write `segments.json` — an array of 5–12 segment objects with `id`, `title`, `time_range`, `summary`, `turn_indices`.

### Important

- Include 200-character overlap between adjacent segments to avoid cutting mid-thought
- Group rapid-fire/lightning-round questions into 1–2 segments, not one per question
- Keep segments chronological; note cross-references in summaries

## Stage 3: Multi-Pass Knowledge Extraction

**Goal:** Extract structured knowledge from each segment using parallel sub-agents, each focusing on one analysis dimension.

### The Six Dimensions

For each segment, extract along these six dimensions (detailed in [references/analysis-framework.md](references/analysis-framework.md)):

| Dimension | Focus | Agent Prompt Key |
|-----------|-------|-----------------|
| 1. Key Topics & Concepts | What is being discussed | Identify structural topics, importance levels |
| 2. Insights & Arguments | Original thinking | Extract frameworks, causal claims, mental models |
| 3. Golden Quotes | Memorable expression | Find verbatim quotable passages with timestamps |
| 4. Data Points & Facts | Evidence | Capture statistics, entities, benchmarks, papers |
| 5. Contradictions & Tensions | Uncertainty | Find self-contradictions, qualifications, doubts |
| 6. Predictions & Forecasts | Forward-looking | Extract future claims with horizons and confidence |

### Parallel Execution Strategy

For a 3-hour interview with ~10 segments, use this fan-out pattern:

1. **Assign 1–2 segments per sub-agent** (e.g., 6 sub-agents, each handling 1–2 segments)
2. **Each sub-agent covers ALL 6 dimensions** for their assigned segments
3. **Provide each sub-agent with:**
   - The transcript text for their segment(s)
   - The full [references/analysis-framework.md](references/analysis-framework.md)
   - Explicit instruction to output structured JSON matching the schemas

### Sub-agent Prompt Template

```
You are extracting structured knowledge from an interview transcript segment.
Read the full segment first, then extract across all 6 dimensions.

Segment: [SEGMENT_TITLE] ([TIME_RANGE])
Transcript text:
[SEGMENT_TEXT]

Using the analysis framework, extract:
1. Key Topics & Concepts
2. Insights & Arguments
3. Golden Quotes (verbatim)
4. Data Points & Facts
5. Contradictions & Tensions
6. Predictions & Forecasts

For each dimension, follow the JSON schema in the framework.
Every item MUST include a source timestamp.
Output your findings as a single JSON object with keys: topics, insights, golden_quotes, data_points, contradictions, predictions.
```

### Quality Check

Spot-check at least 2 extractions against the source transcript. Verify:
- Timestamps are accurate
- Quotes are verbatim
- Insights are attributed correctly (guest's own view vs. reported view)
- No fabricated content

## Stage 4: Synthesize

**Goal:** Merge all segment extractions into a unified knowledge structure and identify cross-cutting themes.

### Process

1. Read all `segment_N_extraction.json` files
2. Merge extractions into a single `knowledge.json` following this schema:

```json
{
  "metadata": { /* from turns.json, enriched with guest bio */ },
  "segments": [
    {
      "id": "seg_01",
      "title": "...",
      "time_range": { "start": "00:00:00", "end": "00:18:45" },
      "summary": "...",
      "key_topics": ["..."],
      "insights": [ { "claim", "explanation", "type", "source_timestamp", "confidence" } ],
      "golden_quotes": [ { "text", "speaker", "timestamp", "context_note", "tags" } ],
      "data_points": [ { "value", "type", "timestamp", "is_estimated", "context" } ],
      "contradictions": [ { "statement_a", "timestamp_a", "statement_b", "timestamp_b", "resolution_note", "type" } ],
      "predictions": [ { "prediction", "time_horizon", "confidence", "conditions", "timestamp" } ]
    }
  ],
  "cross_cutting_themes": [
    { "theme": "...", "description": "...", "appears_in_segments": ["seg_01", "seg_04"], "significance": "..." }
  ],
  "open_questions": ["..."]
}
```

3. **Identify cross-cutting themes**: Patterns that appear across 3+ segments. These are the highest-level takeaways. Examples: "the scaling paradigm is necessary but not sufficient", "practical engineering trumps theoretical elegance"
4. **Resolve contradictions**: Where the same topic is discussed in different segments with apparently conflicting views, determine if it's a real contradiction, a time-horizon difference, or an evolution of thought
5. **Enrich metadata**: Add a 2–3 sentence guest bio based on content from the transcript

### Cross-Cutting Theme Discovery

Ask these questions when merging:
- What argument or framing recurs across multiple segments?
- What does the guest return to even when the interviewer tries to change topics?
- What assumption underlies the guest's answers to seemingly unrelated questions?
- What tension or tradeoff appears in different forms across topics?

## Stage 5: Generate Outputs

**Goal:** Produce all four output formats from `knowledge.json`.

### Output 1: TL;DR Quick Summary

Write directly (no script needed). Use the template in [references/output-templates.md](references/output-templates.md).

- 500–800 words
- 5–7 key takeaways (ordered by importance, not chronology)
- 3–5 golden quotes with timestamps
- Most surprising insight section
- Target audience and reading guide

Save as `tldr-[guest-lastname]-[YYYYMMDD].md`.

### Output 2: Deep-Dive Report

Write directly. Use the full report template in [references/output-templates.md](references/output-templates.md).

- Complete topic-by-topic analysis
- Cross-cutting themes section
- Predictions table
- Complete quote collection
- Reading guide for different reader types

Save as `report-[guest-lastname]-[YYYYMMDD].md`.

### Output 3: Interactive HTML Report

Generate using the script:

```bash
python scripts/generate_html.py knowledge.json --output report-[guest-lastname]-[YYYYMMDD].html
```

The script reads `assets/report-template/` (index.html, style.css, script.js), populates template variables from `knowledge.json`, and writes a self-contained HTML file with all CSS/JS inlined. Features: collapsible sections, search, dark/light theme, timestamp navigation, keyboard shortcuts.

### Output 4: Knowledge Map

Generate using the script:

```bash
python scripts/generate_mindmap.py knowledge.json --output map-[guest-lastname]-[YYYYMMDD].html
```

Produces a self-contained interactive radial mind map (D3.js via CDN). Central node → topic ring → insight ring → quote/data leaf nodes. Features: click to expand/collapse, hover tooltips, zoom/pan, search highlighting.

### Output Directory Convention

Organize outputs by interview:

```
output/
└── [guest-lastname]-[YYYYMMDD]/
    ├── turns.json
    ├── segments.json
    ├── knowledge.json
    ├── tldr-[guest-lastname]-[YYYYMMDD].md
    ├── report-[guest-lastname]-[YYYYMMDD].md
    ├── report-[guest-lastname]-[YYYYMMDD].html
    └── map-[guest-lastname]-[YYYYMMDD].html
```

### Post-Generation Verification (Stage 5b)

After generating all outputs, run the verification checks in [references/quality-checklist.md](references/quality-checklist.md). At minimum:

1. **Open the HTML report** in a browser. Check: search, theme toggle, collapse/expand, sidebar navigation, zero JS errors in console.
2. **Open the mind map** in a browser. Check: 12 topic nodes render, click to expand works, Expand All renders >700 circles, zero JS errors.
3. **Spot-check the TL;DR**: verify all 6 sections present, 5-7 takeaways, quotes have timestamps.
4. **Spot-check the Deep-Dive**: verify all 8 sections present, all 12 segments covered, 3+ quotes spot-checked against knowledge.json for verbatim accuracy.
5. **Run the regression test** from the quality checklist if any template files were modified.

Never deliver outputs without running these checks. See [references/quality-checklist.md](references/quality-checklist.md) for the complete checklist and common pitfall documentation.

## Quality Rules

### Throughout the Pipeline

1. **Every claim must have a source timestamp.** This is non-negotiable. If a timestamp cannot be provided, the claim should not be in the output.
2. **Quotes must be verbatim.** Never paraphrase, clean up, or translate a quote. Use `[...]` for omissions.
3. **No fabricated content.** Never invent claims, data, or quotes. If the guest implies something, mark it as inference.
4. **Flag uncertainty.** If extraction confidence is low, say so. Better to under-claim than over-claim.
5. **Preserve language mixing.** Chinese-English code-switching is common in technical interviews — preserve it in quotes. Summarize in the transcript's primary language.

### Anti-Patterns (Content)

- Summarizing without timestamps
- Paraphrasing quotes
- Creating "topics" that are just the interviewer's questions restated
- Extracting every sentence as a "golden quote"
- Missing cross-cutting themes because each segment was analyzed in isolation
- Generating output formats before the synthesis is complete

### Anti-Patterns (Technical — HTML/JS/CSS)

These are bugs discovered in real usage. Read [references/quality-checklist.md](references/quality-checklist.md) for full details.

1. **`<section>` vs `<details>` mismatch**: `generate_html.py` MUST output `<details open>` + `<summary>` for collapsible topic segments. Using `<section>` breaks the Collapse/Expand buttons silently. This is the #1 most common bug.

2. **DOM reference after removal**: In `clearHighlights()`, NEVER call `m.parentNode.normalize()` after `replaceChild()` — save the parent reference first. Pattern: `var p = m.parentNode; p.replaceChild(newNode, m); p.normalize();`

3. **D3 accessor null guards**: ALL D3 accessor functions (`nodeRadius`, `nodeFill`, `nodeLabel`, etc.) MUST begin with `if (!d || !d.data) return safeDefault;`. Missing guards cause `TypeError: Cannot read properties of undefined` on hierarchy edges.

4. **CSS sticky overlap**: Always set `z-index` on `.sidebar` when `.site-header` is also `position: sticky`. Dynamically set `--header-height` via JS to prevent the sidebar from overlapping the header.

5. **Extraction JSON format drift**: Different sub-agents may use different key names. The merge script MUST handle `topics`/`dimension_1_topics`/nested dict formats. Standardize key names in the extraction prompt.

6. **Windows encoding**: Always write Chinese text to files (never rely on terminal stdout). Provide `--output` flags on all scripts.

## Reference Files

| File | When to Load | Content |
|------|-------------|---------|
| [references/segmentation-guide.md](references/segmentation-guide.md) | Stage 2 | How to split transcripts into topics |
| [references/analysis-framework.md](references/analysis-framework.md) | Stage 3 | Six-dimension extraction taxonomy with JSON schemas |
| [references/output-templates.md](references/output-templates.md) | Stage 5 | Templates for all four output formats |
| [references/quality-checklist.md](references/quality-checklist.md) | Stage 5 (post-generation) | Mandatory QA checks, common pitfalls, regression test script |

## Scripts

| Script | Stage | Purpose |
|--------|-------|---------|
| `scripts/parse_docx.py` | 1 | Extract structured turns from .docx |
| `scripts/generate_html.py` | 5 | Render interactive HTML report from knowledge.json |
| `scripts/generate_mindmap.py` | 5 | Render interactive mind map from knowledge.json |

## Assets

| Asset | Used By | Purpose |
|-------|---------|---------|
| `assets/report-template/index.html` | generate_html.py | HTML report scaffold with template variables |
| `assets/report-template/style.css` | generate_html.py | Editorial design system (light + dark themes) |
| `assets/report-template/script.js` | generate_html.py | Search, navigation, theme toggle, keyboard shortcuts |
| `assets/mindmap-template.html` | generate_mindmap.py | D3.js radial mind map with starfield background |
