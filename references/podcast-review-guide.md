# Podcast Review Guide

Use this guide before running TTS for Output 6.

## Reviewer Role

You are a senior podcast editor reviewing a model-written script for listeners
who do not have time to watch the full interview.

Your job is to decide whether the script works as a real podcast episode, not
whether it merely covers source material.

## Pass Criteria

- The opening sounds like a podcast opening, not task instructions.
- The episode quickly makes clear why this interview matters.
- The script explains what the guest believes, why they believe it, what is
  at stake, and what listeners should remember.
- Ideas are connected by natural reasoning, not by a list of themes.
- Quotes are used sparingly and naturally.
- The script has no spoken timestamps, metadata, markdown artifacts, or
  `HOST:` / `GUEST:` labels.
- No internal prompt or framework language appears in the script.
- The episode does not repeat the same transition or sentence pattern.
- Claims remain faithful to `knowledge.json` and the podcast brief.

## Reject Immediately If

- It sounds like a report outline, source index, or bullet list read aloud.
- It uses phrases such as "从用户角度看", "换成听众最关心的问题",
  "还有一个可以带走的判断", or "这个判断的重点不是概念本身".
- It reads timestamps aloud.
- It repeats the same quote, transition, or explanation.
- It makes a point that does not follow from the source material.
- The opening is generic, flat, or only says "we will summarize this".
- The listener would finish the episode without knowing the guest's core
  opinion.

## Review Output

Return one of:

- `PASS` plus 2-4 short notes on why it works.
- `FAIL` plus specific rewrite instructions. Name the weak paragraphs or
  phrases and explain what should replace them.

If the review returns `FAIL`, revise the script and review again before TTS.
