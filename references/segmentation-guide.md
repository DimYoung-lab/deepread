# Interview Transcript Segmentation Guide

## Purpose

Long interview transcripts (1-3+ hours) cannot be analyzed effectively as a single block of text. This guide provides a systematic method for splitting transcripts into logical topical segments, each suitable for focused analysis. The goal is to preserve thematic coherence while producing segments of manageable size.

---

## Segmentation Heuristics

Apply these four heuristics in combination. No single heuristic is sufficient on its own — reliable boundaries are confirmed by multiple signals.

### 1. Natural Topic Transitions

Speakers often signal topic changes explicitly. Look for these patterns in the transcript:

| Pattern | Chinese Examples | English Examples |
|---------|------------------|------------------|
| Explicit pivot | "接下来我们聊聊...", "那我们换一个话题" | "Let's move on to...", "Let's switch gears" |
| Return reference | "回到刚才说的...", "刚才你提到..." | "Going back to what you said earlier..." |
| Wrap-up signal | "这个问题先到这里", "这个话题差不多了" | "I think we've covered that", "That's a good segue into..." |
| Time boxing | "还有几分钟，我们快速聊一下..." | "We have a few minutes left, let's quickly touch on..." |
| Meta-commentary | "这是今天的最后一个话题" | "This is the last topic for today" |

**Action**: When you encounter these phrases, mark the turn as a candidate segment boundary. These are the strongest signals available.

### 2. Question Pivots

The interviewer's question type shifts in a way that indicates a new thematic category. Signs include:

- **From biographical to technical**: "Where did you grow up?" shifts to "Walk me through the architecture."
- **From broad to specific**: "What's your philosophy on management?" shifts to "How did you handle the Q3 outage?"
- **From present to past/future**: "What are you working on now?" shifts to "Looking back at your early career..."
- **Pre-planned question blocks**: If the interviewer says "I have three areas I want to cover," use that structure.
- **Interviewer restates context**: "Let me give you some context for this next set of questions..." signals a new block.

**Action**: Look for turns where the interviewer speaks for more than 2-3 sentences to set up a new line of questioning. These setup turns are strong boundary markers.

### 3. Timestamp Gaps

Long pauses between turns can indicate a natural break point:

- **Unusually long pauses**: In a transcript where typical turn gaps are 1-3 seconds, a gap of 8-15+ seconds may signal a topic transition (e.g., the interviewer checking notes, a production break).
- **Segment markers in timestamps**: Look for "[00:15:32]" style markers that align with chapter-like structure.
- **Silence annotations**: Transcripts that annotate "(pause)" or "(long pause)" between turns.

**Action**: Scan the transcript's timestamp deltas. Flag any gap that is 3x the median inter-turn interval as a candidate boundary. Validate with heuristic #1 or #2 before committing.

### 4. Keyword Clusters

New technical vocabulary appearing suddenly in the transcript indicates a topic shift:

- **Domain-specific terminology**: A conversation about "user acquisition" shifts to one about "database sharding" — entirely different vocabulary fields.
- **Entity name clusters**: A new set of names (people, companies, products) entering the dialogue.
- **Acronym first-use patterns**: The speaker defines a new acronym, signaling they are entering a new domain.
- **Lexical density change**: The ratio of technical to conversational terms spikes or drops.

**Action**: Track unique nouns and technical terms per 500-character window. A window where >40% of significant terms are novel (not seen in previous windows) is a candidate boundary. This is a quantitative complement to the qualitative heuristics above.

---

## Typical Interview Structure Patterns

Most long-form interviews follow one of these archetypes. Recognizing the pattern early helps anticipate boundaries.

### Pattern A: The Classic Arc (70% of interviews)

| Phase | Duration | Characteristics |
|-------|----------|-----------------|
| Opening / Background | 5-15 min | Introductions, guest bio, how they got started, framing the conversation |
| Main Topic 1 | 15-45 min | Deep dive into primary subject |
| Main Topic 2 | 15-45 min | Second deep dive, often narrower or more specific |
| Main Topic 3 (optional) | 10-30 min | Third topic, typically lighter or forward-looking |
| Lightning Round | 5-10 min | Rapid-fire questions, "this or that", short opinions |
| Closing | 5-10 min | Personal reflections, "anything else?", plugs, goodbyes |

### Pattern B: The Thematic Tour (20% of interviews)

Multiple topics of roughly equal weight, often pre-announced by the interviewer at the start. Each block is 15-30 minutes. The interviewer may enumerate them: "I want to cover A, B, and C today."

### Pattern C: The Conversational Flow (10% of interviews)

Free-flowing, less structured. Topics weave in and out. Harder to segment. Rely more heavily on keyword clusters (heuristic #4) and timestamp gaps (heuristic #3). Accept that some segments will have softer boundaries.

---

## Segment Size Guidelines

| Metric | Value | Rationale |
|--------|-------|-----------|
| **Minimum** | ~2,000 Chinese characters (~600 English words) | Below this, the segment lacks enough substance for meaningful analysis. Consider merging with the adjacent segment. |
| **Maximum** | ~8,000 Chinese characters (~2,400 English words) | Above this, a single analysis pass becomes shallow. Split further if possible. |
| **Target segments** | 5-12 per 3-hour interview | A 3-hour interview at ~5,000 chars/segment yields roughly 6-10 segments. |
| **Overlap** | 200 characters between adjacent segments | Prevents cutting mid-sentence or mid-thought. The overlap text appears in both segments. |

**Merging rule**: If a candidate segment is under 1,200 characters, merge it into the larger of its two neighbors. A segment that small is likely a transitional passage, not a standalone topic.

**Splitting rule**: If a candidate segment exceeds 9,000 characters, look for a sub-topic boundary within it (the guest shifting from "why" to "how", for example). Apply heuristics #1 and #4 internally to find a split point.

---

## Segmentation Process

### Step 1: First Pass — Structural Scan

Read the full transcript (or skim at 3x speed with timestamps). Your goal is to identify the high-level structure. Do not mark detailed boundaries yet.

- Identify which structural pattern (A, B, or C) the interview follows.
- Note any explicit signposting: "We have three topics," "This is part one of two," etc.
- Spot the lightning round and closing sections — these are almost always distinct.

**Output of this step**: A rough outline with 3-6 major thematic blocks.

### Step 2: Mark Candidate Boundaries

Apply all four heuristics systematically against the full transcript:

1. Scan for natural transition phrases (heuristic #1). Highlight every clear instance.
2. Isolate interviewer turns longer than 2 sentences. Check if they pivot topics (heuristic #2).
3. Compute inter-turn timestamp deltas. Flag outliers (heuristic #3).
4. Run a keyword-novelty pass (heuristic #4). Flag high-novelty windows.

Where two or more signals agree on a boundary location, mark it as a **high-confidence boundary**. Where only one signal fires, treat it as a **low-confidence boundary** to be resolved later.

### Step 3: Adjust for Size Constraints

Starting from the first high-confidence boundary, measure the character count between consecutive boundaries:

- **Too short** (< 2,000 chars): Merge with the next segment. Skip the boundary.
- **Too long** (> 8,000 chars): Look for the strongest low-confidence boundary within the oversized block. Promote it to a split point. If none exists, bisect at the nearest interviewer question.
- **Within range**: Keep as-is.

Work from beginning to end. After adjusting, re-measure. The process is iterative — you may need 2-3 passes for a 3-hour transcript.

### Step 4: Name Each Segment

Give each segment a descriptive title in the **transcript's primary language** (Chinese for Chinese-language interviews, English for English, etc.).

Naming conventions:
- Use the guest's own words when they summarize the topic.
- Prefer concrete over abstract: "数据库分库方案" not "技术讨论".
- Include the segment's role when relevant: "开场与背景介绍", "快问快答环节", "结尾寄语".
- Aim for 4-15 characters.

### Step 5: Assign Time Ranges and Turn Indices

For each segment, record:
- **time_range**: Start and end timestamps in `HH:MM:SS` format. Use the timestamp of the first turn in the segment as the start, and the timestamp of the last turn as the end.
- **turn_indices**: The zero-based or one-based index range of turns included. The overlap means the last turn(s) of segment N also appear as the first turn(s) of segment N+1 — reflect this in the indices.

---

## Output Format

Each segment should be represented as a JSON object with the following structure:

```json
{
  "id": "seg_01",
  "title": "嘉宾背景与创业初期经历",
  "time_range": {
    "start": "00:02:15",
    "end": "00:18:40"
  },
  "summary": "Guest describes their education, first startup failure, and lessons learned before founding the current company.",
  "turn_indices": [5, 47]
}
```

Field descriptions:
- **id**: Sequential, zero-padded (`seg_01` through `seg_12`).
- **title**: Descriptive name in the transcript's primary language.
- **time_range**: `start` and `end` in `HH:MM:SS`.
- **summary**: One-line description in English. Maximum 160 characters. Focus on what the segment covers, not meta-commentary.
- **turn_indices**: `[first_turn_index, last_turn_index]` inclusive. Zero-based recommended for programmatic use.

---

## Special Considerations

### Rapid-Fire / Lightning Rounds

Interviews often end with a section of many micro-topics (one question per minute or faster). Do not create one segment per question. Instead:

- **Group the entire lightning round into 1 segment** if it has a clear start signal and is under ~6,000 characters.
- **Split into 2 segments** if the lightning round is unusually long (>8,000 characters) or has a natural midpoint (e.g., personal questions followed by professional ones).
- Name these segments something like "快问快答（上）" and "快问快答（下）" or "Lightning Round — Personal" and "Lightning Round — Professional".

### Topic Revisitation

If the guest returns to a topic discussed earlier:

- **Keep segments chronological.** Do not merge the revisitation into the earlier segment.
- **Note the connection** in the `summary` field: "Revisits hiring challenges first discussed in seg_03, now with focus on remote-team dynamics."
- **Consider a cross-reference** in the earlier segment's summary: "Covers initial hiring struggles; guest returns to this topic in seg_07."

### Dense Technical Discussions

For transcripts heavy on technical detail (architecture walkthroughs, code-level explanations, research paper discussions):

- Use **smaller segments** (closer to 2,000 characters) to keep each concept cluster intact.
- A 45-minute technical deep-dive may need 4-5 segments where a casual conversation of the same length would need only 2.
- Pay extra attention to keyword clusters (heuristic #4) — new technical terms are the strongest signal in technical conversations.

### Casual / Wide-Ranging Conversations

For conversational interviews where topics meander naturally:

- Accept **larger segments** (up to 8,000 characters) to avoid fragmenting the flow.
- Rely more on **interviewer question pivots** (heuristic #2) than on keyword shifts, since the vocabulary may not change dramatically between adjacent topics.
- It is acceptable to have a segment titled "Miscellaneous Topics" or "杂谈" if the content genuinely resists thematic grouping — but limit this to at most one segment per interview.

### Multi-Guest Interviews

For panel discussions or interviews with multiple guests:

- Add an extra consideration: **speaker-turn patterns**. A shift in which guest dominates can signal a topic change.
- Segment boundaries often align with the interviewer directing a question to a different guest.
- The `summary` field should note which guest(s) are the primary speakers in the segment.

---

## Quick Reference Checklist

Before finalizing segments, verify:

- [ ] Each segment has at least 2,000 characters (or a documented reason for being smaller).
- [ ] No segment exceeds 8,000 characters (or has been flagged for follow-up deep-dive).
- [ ] Total segment count is between 5 and 12 for a 3-hour interview.
- [ ] Adjacent segments overlap by approximately 200 characters.
- [ ] Each segment has a descriptive, non-generic title.
- [ ] Time ranges are in valid `HH:MM:SS` format and are monotonically increasing.
- [ ] Turn indices are contiguous (allowing for overlap) and cover the full interview.
- [ ] Lightning round content is grouped, not fragmented.
- [ ] Topic revisitations are noted via cross-reference in summaries.
- [ ] All boundary decisions are backed by at least two heuristics (one is acceptable for Pattern C interviews).
