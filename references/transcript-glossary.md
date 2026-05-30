# Transcript Glossary: Canonical Entities for ASR Correction

## Purpose

This glossary is the canonical reference for correcting garbled entities in ASR (Automatic Speech Recognition) transcripts. Speech-to-text systems frequently mangle proper nouns, technical terms, and domain-specific names. This file maps known garbled variants back to their correct canonical forms, organized by category. Use it during transcript cleaning and entity extraction to resolve ambiguous or corrupted spans.

## How to Use

1. **During transcript correction**: When encountering a suspicious span that does not match known vocabulary, search this glossary for the garbled form.
2. **Disambiguation**: When multiple canonical entities share a variant or when context matters, consult the "Context hints" column.
3. **Extending this glossary**: After each new interview processed, append newly discovered garbled variants to the appropriate category. If a new entity type emerges, add a new category section following the existing format.

## Field Definitions

| Field | Description |
|-------|-------------|
| **Canonical** | The correct, official name or term. |
| **Category** | Entity type: `company`, `product`, `term`, `person`. |
| **Variants** | Known ASR-garbled forms observed in transcripts. List closest matches first. |
| **Context hints** | Adjacent words, topic cues, or speaker patterns that help disambiguate this entity from similar-sounding terms. |

---

## Company / Organization Names

### DeepMind

- **Category**: company
- **Canonical**: DeepMind
- **Variants**: 战木乃伊 (zhan mu nai yi), 宅门 (zhai men), 翟美奶 (di mei nai), 翟母奶 (di mu nai), 张美娜 (zhang mei na), 张奶奶 (zhang nai nai)
- **Context hints**: Mentioned alongside Google, AI research, AlphaGo, reinforcement learning. Often appears when discussing the origin of scaling laws or competing labs.

### Anthropic

- **Category**: company
- **Canonical**: Anthropic
- **Variants**: Anthony, tho pic, hic, 马, 暗消费, authority c, n self hic, on drop c, adobe, sorry
- **Context hints**: Often mentioned with "Claude", "safety", "constitutional AI". Speakers frequently discuss Anthropic alongside OpenAI as a comparison. The "Anthony" variant is particularly common in English segments.

### OpenAI

- **Category**: company
- **Canonical**: OpenAI
- **Variants**: open I, open a, open安, open add, 欧en艾, 欧朋艾 (ou peng ai), 欧朋爱 (ou peng ai), 欧蓬莱 (ou peng lai), 欧派I (ou pai I), 欧盟I (ou meng I), 欧风I (ou feng I), 欧巴 (ou ba), 欧佩拉 (ou pei la)
- **Context hints**: Discussed in context of ChatGPT, GPT series models, Sam Altman, Microsoft partnership. Frequently compared with Anthropic and Google.

### ByteDance / 字节跳动

- **Category**: company
- **Canonical**: ByteDance / 字节跳动 (zi jie tiao dong)
- **Variants**: (no major garbling found in analyzed interviews)
- **Context hints**: Referenced in context of 豆包 (Doubao), Seedance, TikTok, AI video generation. May appear as either "ByteDance" or "字节跳动".

### Google

- **Category**: company
- **Canonical**: Google
- **Variants**: 谷歌 (gu ge) -- this is the standard Chinese name, not a garbled variant. Check context to determine if ASR wrote a garbled English form.
- **Context hints**: Discussed in context of Gemini, DeepMind, search, TPU, cloud infrastructure. Often appears when comparing AI labs.

### Meta

- **Category**: company
- **Canonical**: Meta
- **Variants**: (check context -- may be garbled as "me da", "mei ta", or confused with metadata references)
- **Context hints**: Discussed in context of Llama, open-source AI, social media. Distinguish from the generic term "meta" (as in meta-learning, meta-analysis).

### xAI

- **Category**: company
- **Canonical**: xAI
- **Variants**: XII
- **Context hints**: Associated with Elon Musk, Grok. Often pronounced as "X-A-I" or "xai" in speech.

---

## Product Names

### Claude

- **Category**: product
- **Canonical**: Claude
- **Variants**: cloud, clo
- **Context hints**: Anthropic's AI assistant. Distinguish from "cloud" (cloud computing) by checking for "Anthropic", "model", "AI assistant" nearby. The correct pronunciation is close to "clawed", which ASR may render as "clod" or "claude" (lowercase).

### Gemini

- **Category**: product
- **Canonical**: Gemini
- **Variants**: 张奶奶 (zhang nai nai)
- **Context hints**: Google's AI model. When garbled as 张奶奶, the surrounding context will mention Google, AI model, or comparisons with GPT/Claude. The "张奶奶" variant overlaps with a DeepMind variant -- use company context to disambiguate.

### ChatGPT

- **Category**: product
- **Canonical**: ChatGPT
- **Variants**: (check context -- may be garbled as "chat GBT", "chat GPD", "chat g p t" with scattered characters)
- **Context hints**: OpenAI's consumer product. Often discussed alongside usage statistics, user adoption, or product comparisons. May appear in Chinese as "chat GPT" without translation.

### Codex

- **Category**: product
- **Canonical**: Codex
- **Variants**: code x, 科sir (ke sir)
- **Context hints**: OpenAI's code model. Context involves programming, code generation, developer tools. Distinguish from "codecs" or generic "code" references.

### Seedance

- **Category**: product
- **Canonical**: Seedance
- **Variants**: C-Dance, c dance, C Dance
- **Context hints**: ByteDance's video generation product. Context involves AI video, video generation, ByteDance/字节跳动, Sora competitor.

### SWE-bench

- **Category**: product
- **Canonical**: SWE-bench
- **Variants**: sweet bench, swe bench, 思维班尺 (si wei ban chi)
- **Context hints**: Software engineering benchmark. Context involves coding ability, agent evaluation, software engineering tasks. "SWE" stands for "Software Engineering".

### 豆包 (Doubao)

- **Category**: product
- **Canonical**: 豆包 (Doubao)
- **Variants**: (Chinese name -- less likely to be garbled by Chinese ASR, but verify)
- **Context hints**: ByteDance's AI assistant product. Context involves consumer AI, ByteDance, 字节跳动.

---

## Technical Terms

### scaling law

- **Category**: term
- **Canonical**: scaling law
- **Variants**: skin law, ski NLOW, 异性恋 skin law
- **Context hints**: Discussed in context of model training, compute, parameters, data size. Often appears with "Kaplan", "Chinchilla", or numerical references (10x, 100x). The garbled variant "异性恋 skin law" mixes unrelated Chinese characters with partial English.

### SFT (Supervised Fine-Tuning)

- **Category**: term
- **Canonical**: SFT (Supervised Fine-Tuning)
- **Variants**: SFD, 朴舜 (pu shun)
- **Context hints**: Discussed as a training stage after pre-training, before RLHF. Context includes "fine-tuning", "supervised", "labeled data", "instruction tuning".

### RLHF (Reinforcement Learning from Human Feedback)

- **Category**: term
- **Canonical**: RLHF (Reinforcement Learning from Human Feedback)
- **Variants**: (check context -- may be spelled out or garbled as "RLHF" with letters confused)
- **Context hints**: Discussed as a training stage after SFT. Context includes "human feedback", "reward model", "preference", "PPO", "alignment".

### benchmark

- **Category**: term
- **Canonical**: benchmark
- **Variants**: 班尺码 (ban chi ma), bench mark
- **Context hints**: Context involves evaluation, testing, comparison, scores, metrics. Often followed by specific benchmark names (MMLU, HumanEval, SWE-bench).

### ground truth

- **Category**: term
- **Canonical**: ground truth
- **Variants**: ground choose
- **Context hints**: Context involves data labeling, evaluation, correctness, reference data. Discussed when talking about how to verify model outputs or training data quality.

### postdoc

- **Category**: term
- **Canonical**: postdoc (postdoctoral researcher / position)
- **Variants**: post stock
- **Context hints**: Context involves academic career stages, research training, PhD follow-up. Often appears when discussing researchers' backgrounds or career paths.

### paradigm

- **Category**: term
- **Canonical**: paradigm
- **Variants**: paradise
- **Context hints**: Context involves frameworks, approaches, ways of thinking, paradigm shift. Often appears as "paradigm shift" or "new paradigm".

---

## People Names

### 姚顺宇 (Yao Shunyu)

- **Category**: person
- **Canonical**: 姚顺宇 (Yao Shunyu)
- **Variants**: (guest -- verify name rendering in ASR output; Chinese names are generally well-handled by Chinese ASR)
- **Context hints**: The interview guest. Context involves AI research, scaling laws, DeepMind experience, ByteDance AI.

### 张小珺 (Zhang Xiaojun)

- **Category**: person
- **Canonical**: 张小珺 (Zhang Xiaojun)
- **Variants**: (host -- verify name rendering in ASR output)
- **Context hints**: The interviewer. Asks questions, guides conversation flow. Voice appears in question segments.

### 吴永辉 (Wu Yonghui)

- **Category**: person
- **Canonical**: 吴永辉 (Wu Yonghui)
- **Variants**: (check context)
- **Context hints**: Ex-Google, now at ByteDance. Discussed in context of Google AI, ByteDance AI team, career transitions.

### Dario Amodei

- **Category**: person
- **Canonical**: Dario Amodei
- **Variants**: (check context -- English name in Chinese audio; may be garbled as "Dario", "Dario Amodai", "达里奥")
- **Context hints**: Anthropic CEO. Context involves Anthropic leadership, safety philosophy, scaling, competitor to OpenAI.

### Jared Kaplan

- **Category**: person
- **Canonical**: Jared Kaplan
- **Variants**: (check context -- English name in Chinese audio; may be garbled phonetically)
- **Context hints**: Anthropic co-founder. Often discussed in context of scaling laws research. The name "Kaplan" is strongly associated with the original scaling law paper.

### Sam McCandlish

- **Category**: person
- **Canonical**: Sam McCandlish
- **Variants**: (check context -- English name in Chinese audio; may be garbled phonetically)
- **Context hints**: Anthropic co-founder. Discussed in context of Anthropic founding team.

### Ilya Sutskever

- **Category**: person
- **Canonical**: Ilya Sutskever
- **Variants**: (check context -- English name in Chinese audio; may be garbled as "Ilya", "Sutskever" with various spellings)
- **Context hints**: Ex-OpenAI co-founder and chief scientist. Context involves OpenAI founding, deep learning research, AI safety.

---

## Extension Guide

When adding entities from new interviews, follow this pattern:

```markdown
### Entity Name

- **Category**: company | product | term | person
- **Canonical**: Exact correct name
- **Variants**: variant1, variant2 (pinyin hints where helpful)
- **Context hints**: Specific words, topics, or speaker cues that help disambiguate.
```

### Adding New Categories

If a new interview introduces entity types not covered above (e.g., `conference`, `paper`, `dataset`, `technique`), add a new `##` heading section following the alphabetical ordering convention, and explain the new category in the "How to Use" section if its usage differs from existing categories.

### Variant Collection Process

1. Run the raw transcript through the ASR correction pass.
2. Flag all spans where the transcript output does not match any entry in this glossary or general vocabulary.
3. For each flagged span, determine the canonical entity by listening to the original audio or using context clues.
4. Add the variant to the entity's `Variants` list.
5. If the canonical entity is not yet in the glossary, create a new entry.
