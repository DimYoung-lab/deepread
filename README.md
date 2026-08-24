# deepread · 访谈精读

> 从逐字稿到知识资产 —— 将长篇访谈/播客转录为结构化知识的 AI 技能

[![Skill Type](https://img.shields.io/badge/type-Claude%20Code%20Skill-blue)](https://claude.com/claude-code)
[![Language](https://img.shields.io/badge/lang-中文%20%7C%20English-green)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 解决什么问题

AI 行业的高价值信息，越来越多以 1–3 小时的长访谈、播客形式出现：完整听完一场要一个晚上，听完能复述的观点所剩无几，金句、数据、判断散在几万字的逐字稿里，无法沉淀和复用。

**deepread（访谈精读）** 是一个 Claude Code Skill：把带时间戳的访谈逐字稿（`.docx` / `.txt` / `.md`）变成一套结构化知识产品。它自动完成解析、转录纠错、话题分段、六维知识提取与综合，一次处理产出 7 种形态的内容；每条金句与论点都锚定原文时间戳，可以回查原话。

处理流水线：

```
原始笔录 → 解析 → 校验 → 分段 → 知识提取 → 综合 → 视觉综合 → 生成 → 验证 → 7 种用户可见输出
```

---

## 主要功能

### 7 种输出形态

| 格式 | 说明 | 阅读/收听时间 |
|------|------|---------------|
| 📝 **TL;DR 摘要** | 5-7 个核心观点 + 3-5 条金句 | 10 分钟 |
| 📄 **深度报告** | 完整逐话题分析，原文引用块带时间戳 | 30-45 分钟 |
| 🌐 **学习卡片** | 卡片滑动/主题切换/移动优先 | 通勤学习 |
| 🗺️ **知识图谱** | D3.js 径向思维导图 | 可视化探索 |
| 📱 **社交媒体推文** | 核心观点提炼为社交平台适配格式 | 2 分钟 |
| 🎧 **短播客** | 大模型撰写 + 审稿 + TTS + BGM 混音，最终只保留一个 MP3 | 按原视频长度自适应，约 3-15 分钟 |
| 📕 **精美 PDF** | 中文化、低干扰、紧凑排版的可打印 PDF 版 | 离线阅读/分享 |

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

### 质量机制

- **转录纠错前置**：语音转写在公司名、模型名、人名上的系统性错误，先按术语表精确匹配修正（关闭模糊匹配防误改），全部修改记入 `corrections.json`，逐条可审计，避免错误向下游传导。
- **金句保真**：金句必须是逐字原文且带时间戳，交付前按质量清单抽查回查，杜绝模型「润色」造成的引用失真。
- **播客审稿分离**：写稿与审稿为两个独立角色；审稿分两层——LLM 按听感指南软审，正则脚本按违禁短语黑名单硬检，命中即改稿重审。
- **回归验证**：`references/quality-checklist.md` 固化了覆盖解析、纠错、渲染各环节的回归验证命令，模板变更后手动执行。

---

## 安装方法

### 1. 前置要求

- **Claude Code**：流水线编排 + 知识提取 + Markdown 报告生成
- **Python 3.10+**
- Node.js（仅播客 TTS 需要）

### 2. 安装 Skill

将本仓库克隆到 Claude Code 的 skills 目录：

```bash
# 用户级（所有项目可用）
git clone https://github.com/DimYoung-lab/deepread.git ~/.claude/skills/deepread

# 或项目级（仅当前项目可用）
git clone https://github.com/DimYoung-lab/deepread.git <your-project>/.claude/skills/deepread
```

### 3. 安装依赖

```bash
# Python 依赖（解析 docx、生成 PDF）
pip install python-docx markdown-it-py jinja2 playwright
playwright install chromium

# 可选：播客 TTS（MiniMax Token Plan CLI）
npm install -g mmx-cli
mmx auth login --api-key sk-cp-...
```

浏览器用于查看学习卡片和知识图谱，无需服务器。

---

## 使用方法

### 1. 准备笔录

将访谈的对话文本放入 `transcripts/` 文件夹。转写工具不限，讯飞听见、通义听悟等均可，只要格式为「交替的发言人标识 + 时间戳 + 对话内容」：

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
/deepread
```

### 3. 获得输出

处理完成后，所有输出在 `output/[guest-name]-[interview-date-YYYYMMDD]/` 目录下。目录日期优先使用访谈实际发生日期；无法识别时使用当天日期，不以文件夹创建日期命名。

### 选择性输出与成本预估

- 无需每次生成全部 7 种输出，处理前告知需要哪几种即可，详见 SKILL.md 的「选择性输出模式」章节。
- 运行前可先估算 token 与耗时，再决定跑哪几种形态：

```bash
python scripts/estimate.py transcripts/your-interview.docx
```

---

## 输入输出示例

### 输入

示例访谈：张小珺（语言及世界工作室）对姚顺宇（Google DeepMind 研究员，前 Anthropic，斯坦福物理博士）的深度访谈，时长 3 小时 47 分钟，共 966 轮对话。逐字稿涉及第三方内容版权，不随仓库公开，按上文格式准备自己的笔录即可。

### 输出

```
output/yaoshunyu-20260511/
├── reports/                             ← Markdown 报告
│   ├── tldr-yaoshunyu-20260511.md       ← 10分钟速读
│   ├── report-yaoshunyu-20260511.md     ← 完整深度报告（12 个话题逐段展开）
│   └── social-yaoshunyu-20260511.md     ← 社交媒体推文
├── pdf/                                 ← 精美 PDF
│   ├── report-yaoshunyu-20260511.pdf    ← 12 页
│   └── tldr-yaoshunyu-20260511.pdf      ← 1 页
├── html/                                ← 交互式网页
│   ├── cards-yaoshunyu-20260511.html    ← 学习卡片（9 张卡覆盖 7 个主题）
│   └── map-yaoshunyu-20260511.html      ← 知识图谱
├── audio/                               ← 音频
│   ├── podcast-script-yaoshunyu-20260511.md ← 短播客脚本
│   └── podcast-yaoshunyu-20260511.mp3   ← 最终 BGM 混音播客（约 11 分钟）
├── data/                                ← 中间数据（turns.json、knowledge.json 等）
└── segments/                            ← 分段提取文件
```

姚顺宇场真实处理数据（提取数量随访谈时长与内容密度浮动，仅供参考量级）：

| 指标 | 数值 |
|------|------|
| 对话轮次 | 966 |
| 话题段落 | 12 |
| 提取洞察 | 24 |
| 提取金句 | 36（逐字原文，均带时间戳） |
| 提取预测 | 12 |
| 跨领域主题 | 7 |
| 深度报告原文引用块 | 30+（均带时间戳） |

本场提炼出的 7 个跨领域主题：

1. **AI 的集体主义时代** — 个人英雄主义的终结
2. **范式成熟度三层分化** — 语言→多模态→机器人
3. **资源约束驱动创新** — 算力劣势逼出蒸馏创新
4. **组织 DNA 决定 AI 战略** — Top-Down vs Bottom-Up
5. **AI 产品交互形态远未定型** — Chatbot 不是终局
6. **选择哲学** — 追求本质的难，而非表面的新
7. **Scaling Law 未死** — 从简单堆砌到系统优化

> 姚顺宇场 7 种形态的完整输出已公开在 [`examples/yaoshunyu-20260511/`](examples/yaoshunyu-20260511/)，无需运行即可直接查看；`output/` 为运行时目录，不随仓库公开。

---

## 项目结构

```
deepread/
├── SKILL.md                     ← Skill 入口（流水线编排）
├── README.md                    ← 本文件
├── LICENSE                      ← MIT License
├── .gitignore
├── transcripts/                 ← 原始笔录（Word/txt/md，不随仓库公开）
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
│   ├── estimate.py              ← 运行前 token 与耗时估算
│   └── _mmx_utils.py            ← MiniMax CLI 共享辅助函数
├── references/                  ← 按需加载的参考文档（7 个）
│   ├── analysis-framework.md    ← 6 维提取框架 + JSON 输出结构
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
├── examples/                    ← 公开示例：姚顺宇场 7 种形态的完整输出
└── output/                      ← 运行时输出（全部 gitignored，不随仓库公开）
```

### 文件分类逻辑

| 目录 | 加载时机 | 内容性质 |
|------|----------|----------|
| `SKILL.md` | Skill 触发时 | 流水线编排指令 |
| `references/` | 各阶段按需 | 详细框架和模板（>200行的内容放这里） |
| `scripts/` | 不加载到上下文 | 确定性操作（文件解析、HTML 生成） |
| `assets/` | 脚本读取 | 模板文件，不加载到 LLM 上下文 |
| `transcripts/` | 用户提供 | 原始访谈笔录（不随仓库公开） |
| `output/` | 运行时写入 | 处理产物（不随仓库公开） |

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
- **修改后必须测试**：运行 `references/quality-checklist.md` 中的回归验证

### 质量保证

每次修改模板文件后，执行回归验证（详见 `references/quality-checklist.md`）：

```bash
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

MIT，详见 [LICENSE](LICENSE) 文件。
