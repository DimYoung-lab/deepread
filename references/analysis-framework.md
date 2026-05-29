# Knowledge Extraction Framework

## Purpose

This framework defines the six dimensions of knowledge extraction used during Stage 3 of the interview-based-learning pipeline. Each dimension targets a distinct type of content, ensuring comprehensive coverage without redundancy. Sub-agents use this framework to produce structured JSON output from transcript segments.

---

## Dimension Overview

| # | Dimension | Focus | Key Question |
|---|-----------|-------|-------------|
| 1 | Key Topics & Concepts | Structure | What is being discussed? |
| 2 | Insights & Arguments | Original Thinking | What does the guest believe and why? |
| 3 | Golden Quotes (金句) | Memorable Expression | What is said in a quotable, memorable way? |
| 4 | Data Points & Facts | Evidence | What specific facts, numbers, or entities are referenced? |
| 5 | Contradictions & Tensions | Uncertainty & Debate | Where is there internal conflict, doubt, or qualification? |
| 6 | Predictions & Forecasts | Forward-Looking | What does the guest think will happen? |

---

## Dimension 1: Key Topics & Concepts

### What to Extract

Identify the **structural discussion topics** — what the conversation segment is about at a high level. Distinguish between:

- **Core topics**: The main subject(s) the guest and interviewer spend significant time on. These define the segment's identity.
- **Major topics**: Important sub-themes that receive substantial attention but are not the primary focus.
- **Minor mentions**: Topics touched on briefly or in passing. Worth noting but not central.

### How to Identify

- Look at **question framing** by the interviewer — what they ask about defines the topic
- Look at **sustained attention** — a topic discussed for more than 2-3 consecutive turns is at least "major"
- Look at **explicit naming** — phrases like "the key issue here is..." or "this all comes back to..."
- Distinguish from **examples and tangents** — if the guest uses an anecdote to illustrate a larger point, the larger point is the topic, not the anecdote

### Anti-Patterns

- Listing every noun phrase as a "topic"
- Confusing a single question with a topic (a topic typically spans multiple turns)
- Failing to distinguish between "what is said" and "what it's about"

### Output Schema

```json
{
  "topics": [
    {
      "name": "Model Scaling Laws Debate",
      "description": "Whether transformer scaling laws have hit a wall, including discussion of data bottlenecks, compute limits, and algorithmic improvements.",
      "importance": "core",
      "source_timestamps": ["00:05:30", "00:18:45"],
      "keywords": ["scaling laws", "compute", "data wall", "pre-training"]
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Concise topic label (5–30 characters in transcript language) |
| `description` | string | 1–2 sentence explanation of what the topic covers |
| `importance` | enum: `core` / `major` / `minor` | How central this topic is to the segment |
| `source_timestamps` | array of strings | Timestamps where this topic is discussed (MM:SS or HH:MM:SS) |
| `keywords` | array of strings | 3–8 distinctive terms associated with this topic |

---

## Dimension 2: Insights & Arguments

### What to Extract

The guest's **original thinking** — claims, frameworks, mental models, and reasoning patterns. This is the highest-value dimension: it captures what the reader would miss by not listening to the interview.

### Types of Insights

| Type | Description | Signal Phrases |
|------|-------------|----------------|
| **framework** | A structured way of thinking about a problem | "I think about this in three layers...", "The way I frame it is..." |
| **causal_claim** | An assertion about cause and effect | "X leads to Y because...", "The real reason for Z is..." |
| **counterintuitive** | A claim that contradicts conventional wisdom | "People think X but actually Y", "The surprising thing is..." |
| **analogy** | A comparison that illuminates a concept | "It's like...", "Think of it as...", "The closest parallel is..." |
| **mental_model** | A reusable thinking tool or heuristic | "My rule of thumb is...", "I always ask myself..." |

### How to Identify

- Listen for **assertions of belief**: "I believe...", "My view is...", "I'm convinced that..."
- Listen for **causal chains**: "Because of X, Y happens, which means Z"
- Listen for **generalizations from experience**: "In my experience...", "Every time I've seen..."
- Listen for **challenges to premises**: "The assumption that X is wrong because..."
- Pay special attention to moments where the guest says something the interviewer **did not expect**

### Quality Criteria

- Each insight must be a **claim**, not a topic label
- Each insight must include the **reasoning or evidence** the guest provides (the "why")
- Distinguish between the guest's own view and views they attribute to others
- Flag the confidence level based on how the guest expresses it

### Output Schema

```json
{
  "insights": [
    {
      "claim": "Scaling laws have not hit a fundamental wall — what people are seeing is a data wall, which is an engineering problem, not a theoretical limit.",
      "explanation": "The guest argues that the apparent slowdown in pre-training improvements is caused by running out of high-quality training data, not by any limit in model architecture. He points to continued improvements from better data curation and synthetic data generation as evidence that the scaling paradigm still works.",
      "type": "counterintuitive",
      "source_timestamp": "00:32:15",
      "confidence": "high",
      "related_insights": []
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `claim` | string | The core assertion, one sentence, in the guest's own framing |
| `explanation` | string | 2–4 sentences expanding the reasoning, evidence, and context |
| `type` | enum | One of: `framework`, `causal_claim`, `counterintuitive`, `analogy`, `mental_model` |
| `source_timestamp` | string | Primary timestamp for this insight |
| `confidence` | enum: `high` / `medium` / `tentative` | How confidently the guest asserts this |
| `related_insights` | array of strings | IDs of related insights (cross-references within the segment) |

---

## Dimension 3: Golden Quotes (金句)

### What to Extract

**Verbatim passages** that are quotable out of context. A golden quote is:

1. **Self-contained**: Makes sense without hearing the surrounding conversation
2. **Memorable**: Uses vivid language, a strong opinion, or an elegant formulation
3. **Revealing**: Captures something essential about the guest's worldview or the topic
4. **Compact**: 1–3 sentences; if longer, the core idea should be extractable

### Selection Criteria

- **Prefer** quotes that express a strong, clear opinion
- **Prefer** quotes that would work as a social media post or article pull-quote
- **Prefer** quotes with concrete imagery or specific examples over abstract statements
- **Avoid** quotes that are purely factual (these belong in Data Points)
- **Avoid** quotes that are heavily dependent on the interviewer's question for context
- **Avoid** quotes longer than 4 sentences unless exceptionally dense with insight

### Verbatim Rule (CRITICAL)

Quotes must be **exact transcript text**. Never:

- Paraphrase or "clean up" the wording
- Fix grammar or remove filler words (unless using `[...]` for omission)
- Translate between languages (preserve the original Chinese/English mix)
- Merge sentences from different parts of the transcript

Use `[...]` sparingly to remove digressions or filler. Use `[clarification]` only when a pronoun or reference is genuinely ambiguous without it.

### Output Schema

```json
{
  "golden_quotes": [
    {
      "text": "我觉得很多人对 scaling law 的理解是错的。他们看到 pre-training 的 improvement 在放缓，就说是 scaling law 到头了。但这其实是一个 data wall，不是 compute wall，更不是 algorithmic wall。",
      "speaker": "guest",
      "timestamp": "00:32:15",
      "context_note": "Responding to whether AI progress is slowing down",
      "tags": ["scaling laws", "AI progress", "data wall"],
      "impact": "high"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Verbatim quote text |
| `speaker` | enum: `guest` / `interviewer` | Who said it |
| `timestamp` | string | Exact timestamp (MM:SS or HH:MM:SS) |
| `context_note` | string | 1-sentence setup explaining what question or topic prompted this quote |
| `tags` | array of strings | 2–5 thematic tags for filtering and search |
| `impact` | enum: `high` / `medium` | How striking or revealing the quote is |

---

## Dimension 4: Data Points & Facts

### What to Extract

**Specific, verifiable information** mentioned in the conversation:

- **Statistics**: Numbers, percentages, growth rates, metrics
- **Entities**: Companies, products, people, institutions explicitly named
- **Benchmarks**: Performance comparisons, rankings, evaluation scores
- **Papers**: Academic papers, blog posts, technical reports cited
- **Events**: Historical occurrences, product launches, funding rounds, policy changes
- **Dates**: Specific time references (months, years, quarters)

### How to Identify

- Scan for **numbers**: percentages, dollar amounts, time periods, quantities
- Scan for **proper nouns**: company names, person names, product names (especially in English within Chinese text)
- Scan for **citation language**: "according to...", "I read a paper...", "the benchmark shows..."
- Scan for **temporal markers**: "last year", "in 2024", "Q3", "when I was at [company]"

### Critical: Estimated vs. Cited

Distinguish between:

- **Cited data**: The guest references a specific source (paper, report, benchmark, firsthand knowledge)
- **Estimated data**: The guest gives a rough number, gut feeling, or back-of-the-envelope calculation

This distinction is crucial for readers who may rely on the data.

### Output Schema

```json
{
  "data_points": [
    {
      "value": "Cursor reached ~$100M ARR within 18 months of launch",
      "type": "statistic",
      "timestamp": "01:45:30",
      "is_estimated": true,
      "context": "Discussing how fast AI-native developer tools can scale compared to traditional SaaS",
      "source_quality": "guest_estimate"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The data point, expressed as a complete statement |
| `type` | enum | `statistic`, `entity`, `benchmark`, `paper`, `event`, `date`, `other` |
| `timestamp` | string | Where in the transcript this appears |
| `is_estimated` | boolean | True if the guest is approximating or recalling from memory |
| `context` | string | Why this data point was mentioned |
| `source_quality` | enum: `cited` / `firsthand` / `guest_estimate` / `interviewer_provided` | Reliability of the source |

---

## Dimension 5: Contradictions & Tensions

### What to Extract

Moments of **internal conflict, qualification, or uncertainty** in the conversation. These are often the most intellectually honest and interesting parts of an interview.

### Types of Tension

| Type | Description | Example Signal |
|------|-------------|----------------|
| **self_contradiction** | The guest says something that conflicts with an earlier statement | "Earlier I said X, but actually..." |
| **qualification** | The guest adds important caveats or limitations to their own claim | "But that's only true if...", "The caveat is..." |
| **uncertainty** | The guest explicitly expresses doubt or lack of knowledge | "I don't know", "I'm not sure about that", "We're still figuring out..." |
| **counterargument** | The guest acknowledges the opposing view and engages with it seriously | "The other side would say... and they have a point because..." |

### How to Identify

- Look for **hedging language**: "maybe", "possibly", "it depends", "I could be wrong"
- Look for **explicit self-correction**: "Actually, let me revise that..."
- Look for **acknowledged tradeoffs**: "The downside of this approach is..."
- Look for **unresolved disagreements** with the interviewer
- Pay attention to **long pauses** before answers (may indicate the guest wrestling with a difficult question)

### Why This Matters

Contradictions and tensions often reveal:

- Where the guest's thinking is still evolving
- Where the conventional narrative breaks down
- What the guest considers the hardest or most nuanced problems
- The gap between public messaging and private belief

### Output Schema

```json
{
  "contradictions": [
    {
      "statement_a": "Pre-training improvements are not slowing down — it's a data problem, not a fundamental limit.",
      "timestamp_a": "00:32:15",
      "statement_b": "But I do think we'll need new architectures within the next 2-3 years. You can't just scale transformers forever.",
      "timestamp_b": "01:55:40",
      "resolution_note": "The guest seems to hold both views: scaling still works short-term, but architectural change is needed medium-term. This may not be a true contradiction — it's a time-horizon distinction the interviewer didn't explicitly draw out.",
      "type": "qualification"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `statement_a` | string | The first claim (paraphrased) |
| `timestamp_a` | string | When statement A was made |
| `statement_b` | string | The conflicting or qualifying claim |
| `timestamp_b` | string | When statement B was made |
| `resolution_note` | string | Analysis: is this a real contradiction, a time-horizon difference, or an evolution of thought? |
| `type` | enum | `self_contradiction`, `qualification`, `uncertainty`, `counterargument` |

---

## Dimension 6: Predictions & Forecasts

### What to Extract

**Forward-looking statements** where the guest speculates about future events, trends, or outcomes.

### What to Capture

For each prediction, capture:

1. **What** is being predicted (the specific outcome)
2. **When** it will happen (the time horizon)
3. **How confident** the guest is
4. **What conditions** would change the prediction

### Confidence Levels

| Level | Description | Signal Phrases |
|-------|-------------|----------------|
| **explicit_high** | Guest states high confidence | "I'm very confident that...", "This will definitely happen...", "100%" |
| **explicit_medium** | Guest states moderate confidence | "I think...", "My guess is...", "Probably..." |
| **explicit_low** | Guest states low confidence | "I'm not sure but...", "This is pure speculation...", "Maybe..." |
| **implied** | Guest speaks as if the prediction is obviously true, without hedging | Stated as fact about the future without qualification |

### How to Identify

- Listen for **future-tense claims**: "will", "going to", "by 2027", "in the next few years"
- Listen for **conditional forecasts**: "If X happens, then Y will follow"
- Listen for **timeline predictions**: "I think we'll see AGI in...", "Within N years..."
- Listen for **trend extrapolations**: "At the current rate...", "If this continues..."

### Quality Notes

- A prediction without a time horizon is significantly less useful — note this in the `time_horizon` field
- Distinguish between predictions the guest **wants** to happen and predictions they think **will** happen
- If the guest hedges extensively, the confidence is probably "explicit_low", not "explicit_medium"

### Output Schema

```json
{
  "predictions": [
    {
      "prediction": "Within 18 months, coding will be 99% AI-generated, with humans acting primarily as reviewers and architects.",
      "time_horizon": "18 months (by mid-2027)",
      "confidence": "explicit_high",
      "conditions": "Assumes current rate of coding model improvement continues; would be delayed if reasoning benchmarks plateau.",
      "timestamp": "02:10:30",
      "category": "ai_coding"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | string | The specific predicted outcome |
| `time_horizon` | string | When (e.g., "12-18 months", "by 2028", "within 5 years", "unspecified") |
| `confidence` | enum | `explicit_high`, `explicit_medium`, `explicit_low`, `implied` |
| `conditions` | string | What assumptions does this depend on? What would change it? |
| `timestamp` | string | Where the prediction appears |
| `category` | string | Thematic tag (e.g., `ai_coding`, `industry_structure`, `geopolitics`) |

---

## Cross-Cutting Quality Rules

### 1. Timestamp Attribution (NON-NEGOTIABLE)

Every extracted item **must** include at least one source timestamp. This enables:

- Readers to jump to the exact moment in the original recording
- Verification of extraction accuracy
- Trust in the extraction process

If an insight synthesizes multiple moments in the transcript, include the primary timestamp in `source_timestamp` and secondary timestamps in the `explanation` field.

### 2. Language Preservation

- **Quotes**: Must preserve the exact original language, including Chinese-English code-switching
- **Claims and summaries**: May use whichever language is more natural for the reader, but should preserve key technical terms in their original form
- **Topic names**: Use the transcript's primary language

### 3. No Fabrication

- Never invent claims, data, or quotes that are not in the transcript
- If the guest implies something without stating it, mark it as inference: "The guest implies (but does not state) that..."
- If a data point seems incorrect or outdated, flag it: "The guest states X, though this may refer to [earlier period / different metric]"

### 4. Uncertainty Flagging

- If you're unsure about the accuracy of an extraction, mark it with `"extraction_confidence": "low"` and explain why
- If two reasonable interpretations exist, note both and indicate which you believe is more likely
- When the guest's meaning is genuinely ambiguous, flag it rather than guessing

### 5. Distinguishing Guest View from Reported View

- The guest's own opinion: attribute directly
- The guest reporting what "people say" or "the common view is": attribute as reported view
- The guest reporting their employer's official position: attribute as organizational view
- The guest speculating about others' motivations: attribute as speculation

### 6. Segment Boundary Awareness

- Focus extraction on your assigned segment(s). Do not extract content from outside your segment boundaries.
- If an insight develops across a segment boundary (starts in your segment, continues in the next), extract what's in your segment and note: "Continued in seg_NN"
- The overlap zones (200 characters at segment boundaries) will appear in both segments — it's acceptable for both segments' extractions to reference this content

---

## Extraction Process

### Step 1: Read the Segment

Read your assigned transcript segment(s) fully before extracting anything. Understand the arc: where does the conversation start, where does it go, and where does it end?

### Step 2: Extract Dimension by Dimension

Go through the six dimensions in order. For each dimension:

1. Re-read the segment with that dimension's specific focus
2. Mark candidate extractions (timestamp + initial notes)
3. Apply the quality filters for that dimension
4. Format into the output schema

### Step 3: Cross-Check

After all dimensions are extracted:

- Do the **topics** (Dimension 1) cover all the **insights** (Dimension 2)?
- Do the **quotes** (Dimension 3) support the **insights** (Dimension 2)?
- Do any **contradictions** (Dimension 5) qualify the **predictions** (Dimension 6)?
- Are there insights that don't fit any topic? (If so, you may have missed a topic.)

### Step 4: Prune

Remove low-quality extractions:

- Insights that are obvious or tautological
- Quotes that are mundane or context-dependent
- Data points that are trivial or unverifiable
- Topics that are not actually discussed (just mentioned)

Quality over quantity. 3 excellent insights are more valuable than 15 mediocre ones.

### Step 5: Format and Validate

Ensure your output validates against the JSON schemas above. Double-check all timestamps against the source transcript.
