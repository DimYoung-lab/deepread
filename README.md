# Interview-Based Learning

> 将长篇访谈/播客转录为结构化知识的 AI 技能

[![Skill Type](https://img.shields.io/badge/type-Claude%20Code%20Skill-blue)](https://claude.com/claude-code)
[![Language](https://img.shields.io/badge/lang-中文%20%7C%20English-green)]()

---

## 这是什么？

**Interview-Based Learning** 是一个 Claude Code Skill，专门解决一个痛点：**访谈/播客太长了（1-3小时），没时间听完**。

你只需要提供对话文本（`.docx` / `.txt` / `.md`），它就会自动完成：

```
原始笔录 → 解析 → 校验 → 分段 → 知识提取 → 综合 → 视觉综合 → 生成 → 验证 → 7种用户可见输出
```

### 7 种输出格式

| 格式 | 说明 | 阅读/收听时间 |
|------|------|---------------|
| 📝 **TL;DR 摘要** | 5-7 个核心观点 + 3-5 条金句 | 5 分钟 |
| 📄 **深度报告** | 完整逐话题分析，99+ 引用块 | 30-45 分钟 |
| 🌐 **学习卡片** | 卡片滑动/主题切换/移动优先 | 通勤学习 |
| 🗺️ **知识图谱** | D3.js 径向思维导图 | 可视化探索 |
| 📱 **社交媒体推文** | 核心观点提炼为社交平台适配格式 | 2 分钟 |
| 🎧 **短播客** | 大模型撰写 + 审稿 + TTS + BGM 混音，最终只保留一个 MP3 | 按原视频长度自适应，约 3-15 分钟 |
| 📕 **精美 PDF** | 中文化、低干扰、紧凑排版的可打印 PDF 版 | 离线阅读/分享 |

---

## 快速开始

### 1. 准备笔录

将访谈的对话文本（Word 格式）放入 `transcripts/` 文件夹：

```
transcripts/
└── your-interview.docx
```

转录格式要求：交替的发言人标识 + 时间戳 + 对话内容。例如：

```
发言人1  00:08
今天我们来聊聊AI的未来...

发言人2  00:45
我觉得最关键的问题是...
```

### 2. 触发 Skill

在 Claude Code 中直接说：

> "帮我把 your-interview.docx 处理成知识报告"

或者使用命令：

```
/interview-based-learning
```

### 3. 获得输出

处理完成后，所有输出在 `output/[guest-name]-[interview-date-YYYYMMDD]/` 目录下。这里的 `YYYYMMDD` 优先使用访谈实际发生日期；如果用户没有提供、笔录中也无法识别，则默认使用当天日期。不要用文件夹创建日期作为命名依据。

示例输出（姚顺宇访谈）：

```
output/yaoshunyu-20260511/
├── reports/                             ← Markdown 报告
│   ├── tldr-yaoshunyu-20260511.md       ← 5分钟速读
│   ├── report-yaoshunyu-20260511.md     ← 完整深度报告
│   └── social-yaoshunyu-20260511.md     ← 社交媒体推文
├── pdf/                                 ← 精美 PDF
│   ├── report-yaoshunyu-20260511.pdf
│   └── tldr-yaoshunyu-20260511.pdf
├── html/                                ← 交互式网页
│   ├── cards-yaoshunyu-20260511.html    ← 学习卡片
│   └── map-yaoshunyu-20260511.html      ← 知识图谱
├── audio/                               ← 音频
│   ├── podcast-script-yaoshunyu-20260511.md ← 短播客脚本
│   └── podcast-yaoshunyu-20260511.mp3   ← 最终 BGM 混音播客
├── data/                                ← 中间数据
│   ├── turns.json
│   ├── knowledge.json
│   └── ...
└── segments/                            ← 分段提取
```

---

## 处理流水线

```
Transcript (.docx / .txt / .md)
    │
    ▼
Stage 1: Parse          ── scripts/parse_docx.py         → turns.json
Stage 1.5: Validate     ── scripts/validate_transcript.py → turns-corrected.json
Stage 2: Segment        ── Claude + segmentation-guide    → segments.json
Stage 3: Extract        ── 6 parallel sub-agents          → 12 extraction files
Stage 4: Synthesize     ── Claude merge + cross-cutting   → knowledge.json
Stage 4.5: Visual Synth ── Claude + visual-synthesis-guide→ visual_content.json
Stage 5: Present        ── Claude MD + scripts/generate_*.py → 7 user-facing output formats (可按需选择)
Stage 5b: Verify        ── Claude + quality-checklist     → verified outputs
```

> **提示**：无需每次生成全部 7 种用户可见输出。详见 SKILL.md 中的「选择性输出模式」章节。

### 6 维知识提取

每个话题段落同时从 6 个维度提取：

| 维度 | 提取内容 |
|------|----------|
| 1. 关键话题 | 结构性讨论主题 |
| 2. 洞察与论证 | 原创思维、心智模型、因果论断 |
| 3. 金句 | 可独立引用的原话（带时间戳） |
| 4. 数据与事实 | 统计、实体、基准、论文 |
| 5. 矛盾与张力 | 自我矛盾、限定条件、不确定性 |
| 6. 预测与展望 | 前瞻性声明（含时间窗口和置信度） |

---

## 项目结构

```
interview-based-learning/
├── SKILL.md                     ← Skill 入口（流水线编排）
├── README.md                    ← 本文件
├── .gitignore
├── transcripts/                 ← 原始笔录（Word/txt/md）
│   └── yaoshunyu.docx
├── scripts/                     ← Python 脚本（11 个）
│   ├── parse_docx.py            ← .docx → 结构化 JSON
│   ├── validate_transcript.py   ← 术语校验 + 转录纠错
│   ├── generate_cards.py        ← visual_content.json → 学习卡片
│   ├── generate_mindmap.py      ← visual_content.json → 知识图谱
│   ├── prepare_podcast_brief.py   ← knowledge.json → 播客编导 brief
│   ├── review_podcast_script.py   ← 播客逐字稿 → 审稿硬规则检查
│   ├── generate_audio.py        ← 播客脚本 → TTS 音频
│   ├── generate_bgm_podcast.py  ← 播客音频 → 写回同名 BGM 混音版并清理临时 BGM
│   ├── generate_pdf.py          ← Markdown 报告 → 中文化精美 PDF
│   ├── estimate.py              ← 成本与 token 估算
│   └── _mmx_utils.py            ← MiniMax CLI 共享辅助函数
├── references/                  ← 按需加载的参考文档（7 个）
│   ├── analysis-framework.md    ← 6 维提取框架 + JSON Schema
│   ├── segmentation-guide.md    ← 话题边界检测启发式
│   ├── visual-synthesis-guide.md← 视觉内容综合指南
│   ├── output-templates.md      ← 7 种用户可见输出格式模板
│   ├── podcast-review-guide.md  ← 播客审稿 Agent 标准
│   ├── quality-checklist.md     ← QA 检查清单 + 常见坑位
│   └── transcript-glossary.md   ← 术语表 + 专有名词纠错
├── assets/                      ← 模板与静态资源
│   ├── mindmap-template.html    ← D3.js 知识图谱模板
│   ├── cards-template/
│   │   ├── index.html           ← 学习卡片支架
│   │   ├── style.css            ← 卡片设计系统（亮/暗主题）
│   │   └── script.js            ← 滑动/导航/主题/键盘快捷键
│   └── pdf-templates/           ← PDF 生成模板（中文排版、低干扰线条、紧凑 TL;DR）
│       ├── pdf-style.css        ← 打印设计系统 CSS
│       ├── report-wrapper.html.j2
│       └── tldr-wrapper.html.j2
└── output/                      ← 运行时输出（中间产物 gitignored）
    └── yaoshunyu-20260511/      ← 姚顺宇访谈示例输出（目录日期为访谈日期）
        ├── reports/             ← Markdown 报告（tldr-*.md, report-*.md, social-*.md）
        ├── pdf/                 ← 精美 PDF（report-*.pdf, tldr-*.pdf）
        ├── html/                ← 交互网页（cards-*.html, map-*.html）
        ├── audio/               ← 音频（podcast-script-*.md, podcast-*.mp3；仅 1 个最终 MP3）
        ├── data/                ← 中间数据（turns.json, knowledge.json 等）
        └── segments/            ← 分段提取文件
```

### 文件分类逻辑

| 目录 | 加载时机 | 内容性质 |
|------|----------|----------|
| `SKILL.md` | Skill 触发时 | 流水线编排指令 |
| `references/` | 各阶段按需 | 详细框架和模板（>200行的内容放这里） |
| `scripts/` | 不加载到上下文 | 确定性操作（文件解析、HTML 生成） |
| `assets/` | 脚本读取 | 模板文件，不加载到 LLM 上下文 |
| `transcripts/` | 用户提供 | 原始访谈笔录 |
| `output/` | 运行时写入 | 处理产物 |

---

## 示例：姚顺宇访谈

本仓库包含一个完整的处理示例——张小珺（语言及世界工作室）对姚顺宇（Google DeepMind 研究员，前 Anthropic，斯坦福物理博士）的 3 小时 47 分钟深度访谈。

### 处理统计

| 指标 | 数值 |
|------|------|
| 对话轮次 | 966 |
| 话题段落 | 12 |
| 提取洞察 | 124 |
| 提取金句 | 130 |
| 预测 | 37 |
| 数据点 | 126 |
| 跨领域主题 | 7 |

### 7 个跨领域主题

1. **AI 的集体主义时代** — 个人英雄主义的终结
2. **范式成熟度三层分化** — 语言→多模态→机器人
3. **资源约束驱动创新** — 算力劣势逼出蒸馏创新
4. **组织 DNA 决定 AI 战略** — Top-Down vs Bottom-Up
5. **AI 产品交互形态远未定型** — Chatbot 不是终局
6. **选择哲学** — 追求本质的难，而非表面的新
7. **Scaling Law 未死** — 从简单堆砌到系统优化

---

## 依赖

- **Python 3.10+** + `python-docx`（解析 .docx 文件）
- `markdown-it-py` + `Jinja2` + `playwright`（PDF 生成）
- `mmx-cli`（MiniMax Token Plan CLI，播客 TTS）
- **MiniMax Speech API**（播客 TTS，通过 Token Plan 免流量）
- **Claude Code**（流水线编排 + 知识提取 + Markdown 报告生成）
- 浏览器（查看学习卡片和知识图谱，无需服务器）

安装依赖：

```bash
# Python
pip install python-docx markdown-it-py jinja2 playwright

# MiniMax CLI（播客 TTS）
npm install -g mmx-cli
mmx auth login --api-key sk-cp-...
```

---

## 贡献指南

### 添加新的访谈

1. 将笔录文件放入 `transcripts/`
2. 触发 Skill 处理；如已知访谈实际日期，请提供或写入 `metadata.date`，否则默认使用当天日期
3. 输出自动生成在 `output/` 目录

### 修改 Skill 行为

- **调整提取维度**：编辑 `references/analysis-framework.md`
- **修改输出格式**：编辑 `references/output-templates.md` + 对应 `assets/` 模板
- **改进分段策略**：编辑 `references/segmentation-guide.md`
- **修改后必须测试**：运行 `references/quality-checklist.md` 中的回归测试

### 质量保证

每次修改模板文件后，执行：

```bash
# 回归测试（详见 references/quality-checklist.md）
python -c "import py_compile; py_compile.compile('scripts/parse_docx.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/validate_transcript.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_cards.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_mindmap.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/prepare_podcast_brief.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/review_podcast_script.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_audio.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_bgm_podcast.py', doraise=True)"
python -c "import py_compile; py_compile.compile('scripts/generate_pdf.py', doraise=True)"
```

并在浏览器中验证学习卡片和知识图谱的交互功能，以及生成的 PDF 文件的中文标签、页数、信息密度和排版整洁度。

---

## License

MIT
