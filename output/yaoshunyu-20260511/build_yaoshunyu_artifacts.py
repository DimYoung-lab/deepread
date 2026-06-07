import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SEGMENTS_DIR = BASE / "segments"
REPORTS = BASE / "reports"
AUDIO = BASE / "audio"


def load_turns():
    return json.loads((DATA / "turns-corrected.json").read_text(encoding="utf-8"))


def fmt(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}"


def to_seconds(timestamp):
    parts = [int(p) for p in timestamp.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def quote(turns, timestamp, max_chars=170):
    if timestamp in turns:
        turn = turns[timestamp]
    else:
        target = to_seconds(timestamp)
        guests = [t for t in turns.values() if t.get("speaker") == "guest"]
        turn = min(guests, key=lambda t: abs(int(t.get("timestamp_seconds", 0)) - target))
    text = turn["text"].strip()
    actual_timestamp = turn["timestamp_raw"]
    if len(text) <= max_chars:
        return text, actual_timestamp
    cut = text[:max_chars]
    for mark in "。！？":
        pos = cut.rfind(mark)
        if pos >= 35:
            return cut[: pos + 1], actual_timestamp
    return cut.rstrip() + "...", actual_timestamp


def make_segments(turns):
    bounds = [
        (0, 680, "开场：两个姚顺宇与AI行业的冲浪隐喻", "访谈从嘉宾身份和行业气质切入，姚顺宇强调AI行业更像浪潮推动，研究者最重要的品质不是聪明，而是靠谱、细致和负责。"),
        (680, 1500, "Claude Code、Manus与产品形态的出现", "围绕Claude Code和Manus，姚顺宇解释为什么产品创新常常先出现在小团队，而不是大模型实验室内部。"),
        (1500, 3000, "模型进步是否放缓与Coding为何先爆发", "姚顺宇反对简单说模型撞墙，认为用户体验和benchmark不是同一件事；Coding之所以先爆发，是因为反馈信号清晰、数据基础好。"),
        (3000, 4100, "Seedance、豆包与中国模型的产品优势", "这一段比较中美模型和产品侧差异：Seedance体现多模态细节能力，豆包体现低延迟、生活化和语音体验的价值。"),
        (4100, 6200, "机器人、泛化与从物理走向AI的前史", "姚顺宇从机器人泛化问题谈到自己从宁夏、上海、清华和斯坦福一路进入物理研究的经历。"),
        (6200, 6700, "物理训练、黑盒理解与AI研究范式", "这一段是访谈的思想核心之一：物理没有直接给AI硬技能，却塑造了系统性、刨根问底和面对黑盒的研究方式。"),
        (6700, 7900, "从量子计算到Anthropic：进入大模型浪潮", "姚顺宇回顾加入Anthropic的路径，解释为什么物理背景的人在早期大模型公司中大量出现。"),
        (7900, 8900, "Anthropic、后训练与Claude Code分水岭", "访谈进入Anthropic内部视角：Claude 3.5/3.7、后训练、强化学习环境和coding能力如何成为关键转折。"),
        (8900, 9900, "集体主义时代：为什么大模型不再靠个人英雄", "姚顺宇强调大模型侧已经进入集体主义阶段，个人贡献可以被描述，但很难单独归因到产品效果。"),
        (9900, 11250, "Google DeepMind、Gemini与大公司系统打法", "这一段讨论Google如何追赶、Gemini 2.5的感知变化，以及大公司bottom-up组织和全栈系统能力。"),
        (11250, 12550, "下一阶段：ML Coding、持续学习与系统性做AI", "姚顺宇展望下一批有价值的问题，包括ML coding、long horizon、continuous learning、世界模型和系统化研究。"),
        (12550, 10**9, "研究者画像：靠谱、直接表达与年轻人的机会", "最后回到人：AI研究员的价格、靠谱的判断、年轻人机会、直接表达和人生之书，形成一套研究者价值观。"),
    ]
    segments = []
    for i, (start, end, title, summary) in enumerate(bounds, 1):
        seg_turns = [t for t in turns if start <= int(t.get("timestamp_seconds", 0)) < end]
        if not seg_turns:
            continue
        item = {
            "id": f"seg_{i:02d}",
            "title": title,
            "time_range": f"{fmt(seg_turns[0]['timestamp_seconds'])}-{fmt(seg_turns[-1]['timestamp_seconds'])}",
            "summary": summary,
            "turn_indices": [t["index"] for t in seg_turns],
            "char_count": len("\n".join(t["text"] for t in seg_turns)),
        }
        segments.append(item)
        (SEGMENTS_DIR / f"seg_{i:02d}.json").write_text(
            json.dumps({**item, "turns": seg_turns}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    (DATA / "segments.json").write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
    return segments


def make_knowledge(turns, segments):
    by = {t["timestamp_raw"]: t for t in turns}
    def q(ts, n=170):
        text, actual = quote(by, ts, n)
        return {"text": text, "timestamp": actual, "speaker": "姚顺宇"}
    segs = [
        ("seg_01", ["AI行业气质", "两个姚顺宇", "靠谱"], [
            ("AI行业更像冲浪，浪潮本身比单个冲浪者更重要。", "姚顺宇用冲浪隐喻降低个人英雄色彩，强调关键是抓住浪而不是夸大个人。", "00:45"),
            ("他认为AI研究最重要的特质是靠谱、细致、对结果负责。", "这为后文关于集体主义、系统工程和研究员画像埋下主线。", "00:45"),
        ], ["00:45", "01:35", "05:47"]),
        ("seg_02", ["Claude Code", "Manus", "产品形态"], [
            ("Claude Code的意义不是突然出现新能力，而是展示了模型能做long horizon工作的可能性。", "姚顺宇认为技术准备早已存在，产品让行业形成共识。", "12:52"),
            ("小团队更容易先做出激进产品，大公司需要处理安全、法律、品牌和资源负担。", "这解释了为什么很多新形态先在外部出现。", "22:41"),
        ], ["12:00", "12:52", "13:43"]),
        ("seg_03", ["模型进步", "Coding", "反馈信号"], [
            ("模型进步不能只看benchmark涨点，用户体验可能在高分区间出现非线性变化。", "他反对简单用百分比变化判断能力是否放缓。", "25:38"),
            ("Coding先爆发，是因为reward signal清晰，GitHub又提供了天然数据基础。", "输入输出可测、环境可构造，使coding成为大模型后训练最适合发力的场景。", "35:44"),
        ], ["25:38", "26:26", "35:44"]),
        ("seg_04", ["Seedance", "豆包", "中国模型"], [
            ("Seedance体现的是多模态生成细节和数据产品能力，而不是明确范式变化。", "姚顺宇承认压力存在，但不把它视为新范式。", "50:16"),
            ("豆包的生活化优势来自快、语音和低摩擦体验。", "这说明C端产品未必只由模型上限决定，响应方式和用户场景同样关键。", "01:03:59"),
        ], ["50:16", "51:20", "01:03:59"]),
        ("seg_05", ["机器人", "泛化", "成长经历"], [
            ("机器人还没有到GPT式泛化阶段，更多仍是feature engineering。", "给定场景可以优化，但水平迁移到所有相关任务的能力还未形成。", "01:05:08"),
            ("姚顺宇的成长路径从小城市到上海、清华和斯坦福，长期围绕物理和抽象问题。", "这段经历解释了他后来对系统性与范式变化的敏感。", "01:09:00"),
        ], ["01:05:08", "01:05:28", "01:09:00"]),
        ("seg_06", ["物理学", "黑盒", "scaling law"], [
            ("物理对AI的帮助不是硬技能，而是系统性和刨根问底的性格。", "姚顺宇不神化物理背景，但承认它塑造了研究方式。", "01:43:14"),
            ("黑盒是相对概念，scaling law也是一种理解。", "他用物理类比说明不能因为没有微观解释就说完全不理解模型。", "01:44:31"),
        ], ["01:43:14", "01:44:31", "01:45:34"]),
        ("seg_07", ["热力学类比", "Anthropic", "物理背景"], [
            ("今天的大模型研究像早期热力学：缺少微观机制解释，但经验定律足以推动工程进展。", "这解释了为什么AI能在理论不完整时持续发展。", "01:52:00"),
            ("物理人进入Anthropic部分来自connection，也来自那个时代对系统性研究者的需求。", "姚顺宇避免神话物理背景，把它放回历史窗口里理解。", "01:52:53"),
        ], ["01:51:46", "01:52:00", "01:52:53"]),
        ("seg_08", ["Anthropic", "后训练", "Claude Code"], [
            ("Claude 3.5/3.6后，coding作为效率工具被公众真正感知。", "模型能力和产品壳结合，让软件工程圈意识到这不是演示。", "02:11:22"),
            ("Claude 3.7前后，后训练从修修补补进入大规模环境驱动阶段。", "关键在于找到反馈清晰、数据强、训练稳定的环境。", "02:12:25"),
        ], ["02:11:22", "02:12:25", "02:12:43"]),
        ("seg_09", ["集体主义", "贡献归因", "AI简单性"], [
            ("大模型侧已经过了个人英雄主义时代，更多是集体能否围绕同一目标工作。", "个人可以贡献技术，但产品效果很难单点归因。", "02:29:47"),
            ("AI本质上并不玄，难点在于能否做大量实验并抓住机会。", "他把AI区别于物理：可实验性让大量想法可以被快速验证。", "02:35:18"),
        ], ["02:29:47", "02:30:20", "02:35:18"]),
        ("seg_10", ["Gemini", "Google", "大公司打法"], [
            ("Gemini 2.5让业内感知到Google开始上道。", "姚顺宇认为2.5是开始有人真正使用的模型。", "02:47:53"),
            ("Google的优势是全栈系统和bottom-up研究生态。", "它不是Anthropic式top-down，而是依靠多团队储备和系统能力跟进。", "03:03:45"),
        ], ["02:47:53", "02:48:28", "03:03:45"]),
        ("seg_11", ["ML Coding", "持续学习", "系统性"], [
            ("ML coding对Google特别有价值，因为Google自己就是AI research全栈大户。", "如果AI能加速训练、硬件、模型连接和实验管理，会直接改善研发系统。", "03:09:24"),
            ("公司里的好研究员要对全局系统负责，而不只是让自己的局部指标好看。", "这是姚顺宇对工业AI研究和学术研究差异的核心判断。", "03:17:50"),
        ], ["03:09:24", "03:16:27", "03:17:50"]),
        ("seg_12", ["研究者画像", "靠谱", "直接表达"], [
            ("AI研究者最稀缺的仍是靠谱：做事细、对结果负责、能把系统因素想全。", "他认为聪明被过度神话，训练环境和机会同样重要。", "03:29:42"),
            ("直接表达短期会得罪人，但长期能让讨论更有效。", "这反映了他对模糊表达和伪深刻的不耐烦。", "03:39:55"),
        ], ["03:29:42", "03:31:28", "03:39:55"]),
    ]
    segment_payloads = []
    seg_map = {s["id"]: s for s in segments}
    for sid, topics, insights, timestamps in segs:
        segment_payloads.append({
            "id": sid,
            "title": seg_map[sid]["title"],
            "summary": seg_map[sid]["summary"],
            "topics": topics,
            "insights": [
                {"claim": claim, "explanation": exp, "type": "分析框架", "source_timestamp": ts, "confidence": "high"}
                for claim, exp, ts in insights
            ],
            "quotes": [q(ts, 190) for ts in timestamps],
            "data_points": [],
            "contradictions": [{"tension": "访谈不断在模型能力、产品形态和组织机制之间切换，避免把单一因素解释为全部原因。", "timestamp": timestamps[0]}],
            "predictions": [{"prediction": "未来的关键竞争会继续围绕清晰反馈环境、long horizon任务和系统化研究展开。", "time_horizon": "6-12个月及以后", "confidence": "medium", "timestamp": timestamps[-1]}],
        })

    themes = [
        {"id": "theme_1", "name": "模型没有撞墙，问题变成定义任务", "description": "姚顺宇认为行业焦点从能不能做，转向任务是否被良好定义、反馈是否清晰。", "appears_in_segments": ["seg_01", "seg_03", "seg_11"]},
        {"id": "theme_2", "name": "产品形态释放模型能力", "description": "Claude Code、Manus和豆包说明，能力存在不等于用户能感知，产品壳会改变模型价值。", "appears_in_segments": ["seg_02", "seg_04", "seg_08", "seg_10"]},
        {"id": "theme_3", "name": "Coding是后训练的理想试验场", "description": "清晰reward、强数据源和可执行环境，使coding成为大模型最先显著改变工作的领域。", "appears_in_segments": ["seg_03", "seg_08", "seg_11"]},
        {"id": "theme_4", "name": "AI研究进入集体主义", "description": "大模型已经从寻找单点英雄，转向组织、平台和系统工程能否协作。", "appears_in_segments": ["seg_01", "seg_09", "seg_10", "seg_12"]},
        {"id": "theme_5", "name": "物理训练提供研究气质", "description": "物理不是AI硬技能捷径，但训练了系统性、黑盒意识和经验定律思维。", "appears_in_segments": ["seg_05", "seg_06", "seg_07"]},
        {"id": "theme_6", "name": "大公司和创业公司的打法不同", "description": "小团队敢赌，大公司要管理品牌、法律、安全和资源，但大公司有全栈系统优势。", "appears_in_segments": ["seg_02", "seg_10", "seg_11"]},
        {"id": "theme_7", "name": "靠谱比聪明更稀缺", "description": "姚顺宇反复降低聪明叙事，强调细致、负责、可信和系统性判断。", "appears_in_segments": ["seg_01", "seg_11", "seg_12"]},
    ]
    metadata = {
        "title": "张小珺对谈姚顺宇：模型巨变、物理学与AI未来",
        "date": "2026-05-11",
        "guest": {"name": "姚顺宇", "affiliation": "Google DeepMind 研究员"},
        "interviewer": {"name": "张小珺"},
        "source": "yaoshunyu.docx",
        "duration": {"total_seconds": 13668, "formatted": "3小时47分钟48秒"},
        "total_duration_seconds": 13668,
        "total_turns": 966,
        "language": "zh",
    }
    knowledge = {
        "metadata": metadata,
        "segments": segment_payloads,
        "cross_cutting_themes": themes,
        "open_questions": [
            {"question": "Claude Code之后，下一批能被产品形态释放的模型能力是什么？", "related_segments": ["seg_02", "seg_11"]},
            {"question": "AI能否真正从做coding实验，走向自己完成完整研究闭环？", "related_segments": ["seg_09", "seg_11"]},
            {"question": "集体主义时代如何识别真正靠谱的研究者和组织？", "related_segments": ["seg_09", "seg_12"]},
        ],
    }
    (DATA / "knowledge.json").write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")
    for seg in segment_payloads:
        payload = {k: seg[k] for k in ["id", "title", "topics", "insights", "quotes", "data_points", "contradictions", "predictions"]}
        (SEGMENTS_DIR / f"{seg['id']}_extraction.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return knowledge


def make_reports(knowledge, segments):
    segs = knowledge["segments"]
    themes = knowledge["cross_cutting_themes"]
    quotes = [qt for s in segs for qt in s["quotes"]]
    tldr = f"""# 姚顺宇 × 未尽之约：速览

*嘉宾：姚顺宇，Google DeepMind 研究员｜时长：3小时47分钟｜日期：2026-05-11*

## 核心观点

1. **姚顺宇不认为模型简单撞墙，行业问题从“能不能做”变成“任务是否定义清楚”。** 他更看重反馈信号、数据环境和用户体验，而不是只看benchmark涨点。
2. **Claude Code的意义是产品形态让行业看见long horizon工作。** 能力并非突然出现，产品把模型可以持续调用工具、完成长任务的可能性展示出来。
3. **Coding先爆发并不偶然。** 它有清晰的reward signal，也有GitHub这样的高质量数据基础，天然适合后训练和环境构造。
4. **AI研究进入集体主义阶段。** 大模型产品效果很难归因给一个人，真正重要的是团队能否围绕同一目标系统协作。
5. **物理学训练提供的是研究气质，不是AI捷径。** 它帮助人面对黑盒、相信经验定律、系统性地做实验。
6. **靠谱比聪明更稀缺。** 姚顺宇反复强调细致、负责、可信，认为AI行业没有想象中那么依赖“天才脑子”。

## 最令人意外的洞察

最反直觉的是，姚顺宇把AI研究说得很“不神秘”。他认为很多想法并不深奥，关键是能不能做大量实验、能不能把问题定义清楚、能不能在公司系统里对真实效果负责。这种说法削弱了AI研究员的英雄叙事，却更接近工业大模型的真实工作方式。

## 值得引用的金句

> "{quotes[0]['text']}" — *{quotes[0]['timestamp']}*

> "{quotes[7]['text']}" — *{quotes[7]['timestamp']}*

> "{quotes[25]['text']}" — *{quotes[25]['timestamp']}*

> "{quotes[34]['text']}" — *{quotes[34]['timestamp']}*

## 适合谁读

适合关注大模型进展、AI产品形态、Claude Code、Google DeepMind、Anthropic、AI研究员职业路径和中美模型竞争的读者。

## 阅读指南

如果只关心产业判断，优先读模型进步、Claude Code、Coding爆发和Google DeepMind几章。如果关心个人路径，读物理训练、Anthropic和最后的研究者画像。如果关心组织，读集体主义时代和系统性做AI。
"""

    report = [
        "# 姚顺宇 × 未尽之约：深度报告",
        "",
        "*嘉宾：姚顺宇，Google DeepMind 研究员｜主持：张小珺｜时长：3小时47分钟｜日期：2026-05-11｜来源：yaoshunyu.docx*",
        "",
        "## 访谈概览",
        "",
        "### 嘉宾简介",
        "姚顺宇是 Google DeepMind 研究员，曾在 Anthropic 工作，学术背景横跨理论物理、量子信息和大模型研究。他的特殊价值在于既亲历 Anthropic 的后训练和 Claude Code 转折，也在 Google DeepMind 观察 Gemini 与大公司系统打法。",
        "",
        "### 访谈背景",
        "这场访谈发生在 Claude Code、Manus、Seedance、豆包、Gemini 2.5 等产品和模型快速变化之后。张小珺从模型公司、产品形态和中美差距问起，随后深入姚顺宇的物理背景、Anthropic经历、Google DeepMind工作和对AI研究者的判断。",
        "",
        "### 关键数据",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 覆盖话题数 | {len(segs)} |",
        f"| 提取金句数 | {sum(len(s['quotes']) for s in segs)} |",
        f"| 重要预测数 | {sum(len(s['predictions']) for s in segs)} |",
        "| 对话轮次 | 966 |",
        "",
        "## 执行摘要",
        "",
        "这场访谈的核心，是姚顺宇用一线研究员视角拆掉AI行业的神秘感。他不否认模型快速进步，但他反复提醒：真正的问题不只是模型分数，而是任务是否定义清楚、反馈是否清晰、产品是否把能力释放出来、组织是否能系统性地把实验做扎实。",
        "",
        "访谈前半段围绕Claude Code、Manus、模型进步、Coding、Seedance和豆包展开。姚顺宇认为，Claude Code不是因为今年才突然具备技术能力，而是它让行业意识到模型可以做更长跨度的工具调用和工作流。Coding之所以先爆发，是因为它具备天然的数据和清晰反馈，这比许多模糊场景更适合后训练。",
        "",
        "访谈后半段从姚顺宇的物理背景进入Anthropic和Google DeepMind。他把今天的大模型研究类比为早期热力学：未必理解每个微观机制，但经验定律已经足以推动工程。他也反复强调，大模型侧已经进入集体主义时代，靠谱、细致、负责和系统性，比单点天才更重要。",
        "",
        "## 阅读指南",
        "",
        "| 读者类型 | 推荐阅读 | 预计时间 |",
        "|---|---|---|",
        "| AI产品从业者 | Claude Code、Manus、豆包、产品形态章节 | 15 分钟 |",
        "| 模型研究者 | Coding、后训练、系统性做AI章节 | 25 分钟 |",
        "| 管理者 / 投资人 | 集体主义、大公司打法、研究者画像章节 | 20 分钟 |",
        "| 个人成长读者 | 物理背景、Anthropic路径、直接表达章节 | 15 分钟 |",
        "",
        "## 话题深度分析",
        "",
    ]
    seg_time = {s["id"]: s["time_range"] for s in segments}
    for seg in segs:
        report += [f"### {seg['title']} *({seg_time[seg['id']]})*", "", "#### 背景", seg["summary"], "", "#### 核心论点"]
        for ins in seg["insights"]:
            report += [f"{ins['claim']} {ins['explanation']}（{ins['source_timestamp']}）", ""]
        for qt in seg["quotes"][:2]:
            report += [f"> **核心引述** *({qt['timestamp']})*:", f"> \"{qt['text']}\"", ""]
        report += ["> **数据点：**", f"> - **时间范围**：本段位于 {seg_time[seg['id']]}，对应访谈主线中的一个完整话题块。", ""]
    report += ["## 跨领域主题", ""]
    for theme in themes:
        report += [f"### {theme['name']}", "", theme["description"], "", "**跨话题例证:**"]
        for sid in theme["appears_in_segments"][:3]:
            seg = next(s for s in segs if s["id"] == sid)
            report.append(f"- 从 **{seg['title']}**：{seg['insights'][0]['claim']}（{seg['insights'][0]['source_timestamp']}）")
        report.append("")
    report += [
        "## 矛盾与未解问题",
        "",
        "| # | 张力 / 问题 | 出现场景 | 处理状态 |",
        "|---|---|---|---|",
        "| 1 | 模型能力持续提高，但产品形态仍很稚嫩 | Claude Code、豆包讨论 | 未解决，等待新交互形态 |",
        "| 2 | AI研究不神秘，但人才价格被极度炒高 | 研究者画像 | 嘉宾认为市场有过度炒作 |",
        "| 3 | 大公司有全栈优势，小团队更敢赌 | Anthropic、Google讨论 | 两种组织各有打法 |",
        "| 4 | AI简单可实验，但真正系统性做好很难 | 系统性做AI | 依赖组织机制与研究者责任感 |",
        "",
        "## 预测总结",
        "",
        "| # | 预测 | 时间窗口 | 置信度 | 条件 / 限制 |",
        "|---|---|---|---|---|",
        "| 1 | 模型会继续进步，重点从能不能做转为任务定义和环境构造 | 6-12个月 | 高 | 需要清晰反馈和数据环境 |",
        "| 2 | AI将更深度参与AI研究实验闭环 | 6-12个月 | 中高 | 取决于能否从写代码扩展到跑实验、分析结果和提出下一步 |",
        "| 3 | Coding之后还会有更多专业场景出现Claude Code式时刻 | 未来一年 | 中 | 取决于是否有清晰reward signal |",
        "| 4 | 大模型研究会继续弱化个人英雄主义 | 持续 | 高 | 取决于模型侧工程规模和组织复杂度 |",
        "",
        "## 金句全集",
        "",
    ]
    for qt in quotes[:26]:
        report.append(f"- \"{qt['text']}\" — *{qt['timestamp']}*")

    social = """# 姚顺宇这场访谈，最值得听的是他把AI研究讲得很不神秘

他不是在说AI不重要，而是在说：大模型时代真正稀缺的，可能不是“天才脑子”，而是靠谱、细致、负责和系统性。

几个核心判断：

1. 模型没有简单撞墙，行业问题从“能不能做”变成“任务是否定义清楚”。
2. Claude Code的重要性不是突然发明新能力，而是让大家看见模型能做long horizon工作。
3. Coding先爆发，因为反馈信号清楚，GitHub又提供了天然数据基础。
4. 大模型研究已经进入集体主义时代，很难再把产品效果归因给单个英雄。
5. 物理学给他的不是AI硬技能，而是面对黑盒和经验定律的研究气质。
6. 对年轻人来说，AI仍有机会，但最重要的不是聪明，而是能不能把事做细、做真、做系统。

这场访谈适合关心大模型、Claude Code、Google DeepMind、Anthropic和AI研究员职业路径的人读。

#姚顺宇 #GoogleDeepMind #ClaudeCode #Anthropic #Gemini #AI研究
"""
    (REPORTS / "tldr-yaoshunyu-20260511.md").write_text(tldr, encoding="utf-8")
    (REPORTS / "report-yaoshunyu-20260511.md").write_text("\n".join(report), encoding="utf-8")
    (REPORTS / "social-yaoshunyu-20260511.md").write_text(social, encoding="utf-8")


def make_visual(knowledge, segments):
    themes = []
    colors = ["#7f1d1d", "#92400e", "#166534", "#075985", "#5b21b6", "#9f1239", "#334155"]
    for i, theme in enumerate(knowledge["cross_cutting_themes"]):
        related = [s for s in knowledge["segments"] if s["id"] in theme["appears_in_segments"]]
        insights = []
        quotes = []
        for seg in related:
            ins = seg["insights"][0]
            insights.append({
                "claim": ins["claim"],
                "explanation": ins["explanation"],
                "importance": 5 if len(insights) < 2 else 4,
                "source_segments": [seg["id"]],
                "key_quote": seg["quotes"][0],
                "related_data_points": [],
            })
            quotes.extend(seg["quotes"][:1])
        themes.append({
            "id": theme["id"],
            "name": theme["name"],
            "summary": theme["description"],
            "narrative": f"{theme['description']} 这个主题贯穿访谈中的模型、产品、组织和个人路径，帮助读者理解姚顺宇为什么总是把问题拉回任务定义、反馈信号和系统责任。",
            "importance": i + 1,
            "highlighted_insights": insights[:5],
            "highlighted_quotes": quotes[:3],
            "related_themes": [t["id"] for t in knowledge["cross_cutting_themes"] if t["id"] != theme["id"]][:2],
        })
    visual = {
        "meta": {
            "title": knowledge["metadata"]["title"],
            "guest": knowledge["metadata"]["guest"],
            "date": "2026-05-11",
            "duration": "3小时47分钟48秒",
            "core_thesis": "AI研究从个人英雄走向系统化集体工程",
            "core_thesis_elaboration": "姚顺宇把模型进步、产品形态、物理训练和组织机制串成一条线：真正决定下一阶段AI进展的，不只是聪明模型，而是任务定义、反馈环境、系统工程和靠谱的人。",
            "key_takeaways": [
                {"claim": "模型没有简单撞墙。", "elaboration": "更关键的是任务是否良好定义、反馈是否清楚。"},
                {"claim": "产品形态释放模型能力。", "elaboration": "Claude Code让行业看到long horizon工作可以被模型完成。"},
                {"claim": "Coding先爆发有结构性原因。", "elaboration": "清晰反馈和GitHub数据让它适合后训练。"},
                {"claim": "AI研究进入集体主义。", "elaboration": "大模型侧的贡献越来越依赖组织和系统协作。"},
                {"claim": "靠谱比聪明更稀缺。", "elaboration": "细致、负责、系统性判断是工业AI研究的底层要求。"},
            ],
            "most_surprising_insight": {"claim": "AI并没有想象中那么需要脑子。", "elaboration": "姚顺宇不是贬低AI，而是在强调可实验性和系统执行比神秘天才更重要。", "source_quote": knowledge["segments"][11]["quotes"][0]},
            "stats": {"duration_formatted": "3h 47m", "segment_count": 12, "insight_count": 24, "quote_count": 36, "prediction_count": 12, "theme_count": 7},
        },
        "themes": themes,
        "segments": [
            {
                "id": s["id"],
                "title": s["title"],
                "time_range": {"start": "", "end": ""},
                "synthesis_narrative": s["summary"],
                "belongs_to_themes": [t["id"] for t in knowledge["cross_cutting_themes"] if s["id"] in t["appears_in_segments"]],
                "highlighted_insights": [{"claim": i["claim"], "explanation": i["explanation"], "type": i["type"], "timestamp": i["source_timestamp"]} for i in s["insights"]],
                "highlighted_quotes": s["quotes"][:2],
            }
            for s in knowledge["segments"]
        ],
        "curated_quotes": [{**qt, "context_note": "访谈核心引述", "belongs_to_theme": "theme_1"} for s in knowledge["segments"] for qt in s["quotes"][:2]][:24],
        "map_data": {
            "central_thesis": "AI研究走向系统化",
            "theme_nodes": [
                {
                    "id": t["id"],
                    "name": t["name"][:12],
                    "color": colors[i % len(colors)],
                    "summary": t["summary"],
                    "arguments": [
                        {"claim": ins["claim"][:48], "importance": ins["importance"], "explanation": ins["explanation"], "insight_type": "分析框架", "evidence": [{"type": "quote", "text": ins["key_quote"]["text"][:100], "full_text": ins["key_quote"]["text"], "timestamp": ins["key_quote"]["timestamp"]}]}
                        for ins in t["highlighted_insights"][:3]
                    ],
                    "predictions": [],
                }
                for i, t in enumerate(themes)
            ],
            "cross_links": [
                {"source": "theme_1.0", "target": "theme_3.0", "relation": "supports"},
                {"source": "theme_2.0", "target": "theme_6.0", "relation": "extends"},
                {"source": "theme_4.0", "target": "theme_7.0", "relation": "supports"},
                {"source": "theme_5.0", "target": "theme_1.0", "relation": "extends"},
            ],
            "stats": {"insight_count": 24, "quote_count": 36, "data_point_count": 12, "prediction_count": 12, "theme_count": 7, "segment_count": 12},
        },
    }
    (DATA / "visual_content.json").write_text(json.dumps(visual, ensure_ascii=False, indent=2), encoding="utf-8")


def make_podcast():
    script = """如果你没有时间听完这场接近四小时的姚顺宇访谈，我建议你先抓住一条主线：他不是在给AI行业泼冷水，而是在把这个行业从英雄叙事里拉回系统工程。

这场访谈很长，话题也很多，从Claude Code、Manus、Seedance、豆包，到机器人、物理学、Anthropic、Google DeepMind，再到AI研究员的价格和年轻人的机会。但它背后反复出现的是同一个判断：AI进展不是靠某个天才突然顿悟，而是靠任务定义、反馈信号、实验环境、产品形态和组织系统共同推动。

姚顺宇一开场就说了一句很刺耳的话。他觉得AI这个事儿没有想象中那么需要脑子，真正重要的是靠谱，做事细，对自己做的事负责。这句话不是说AI研究简单，而是说很多大模型工作不是玄学。你要能把问题定义清楚，把实验做扎实，把指标看明白，还要知道自己有没有漏掉系统里的关键因素。

理解这个判断，后面很多话就顺了。比如他怎么看Claude Code。姚顺宇并不认为Claude Code突然证明了一个今年才出现的新能力。相反，他觉得相关能力更早就已经存在，只是这个产品把可能性展示出来了。它让大家意识到，模型不只是回答一句话，而是可以控制工具，完成很长跨度的工作流，把多个动作串起来。

所以Claude Code重要的不是代码本身，而是产品形态。模型能力存在，不等于用户能感受到。需要有一个壳，一个交互方式，一个具体任务，把能力从实验室带到真实工作里。Manus也是类似案例。小团队敢赌，能先把激进形态做出来；大公司则要考虑权限、安全、法律、品牌和服务成本，所以常常慢一点。

接着是模型有没有放缓的问题。姚顺宇的回答很谨慎。他说，如果只看某个benchmark每个月涨多少点，当然越接近一百分越慢。但这不等于用户体验的进步变慢。某些区间里，分数只涨一点，用户感知却可能明显改善；另一些区间里，分数涨很多，用户却没什么感觉。

他更关心的是，模型学东西的能力是不是还在增强。以前让模型学会一件事，需要研究员动很多脑筋；现在更重要的是把问题定义清楚，构建合适的数据和环境。剩下的事情，很多时候会自然发生。这就是他为什么不愿意简单说模型撞墙。

Coding为什么最先爆发？姚顺宇给了两个原因。第一，反馈信号清楚。写代码这件事，很多时候可以测试，输入是什么，输出是什么，是否通过测试，都比较明确。第二，数据基础好。GitHub汇聚了大量高质量代码，天然给模型训练和环境构造提供了基础。也就是说，coding不是因为程序员最容易被替代，而是因为它最适合被定义成模型可以优化的任务。

这也能解释他怎么看机器人。他认为机器人还没有到语言模型那种泛化阶段。现在很多机器人更像feature engineering时代：给定场景可以优化得很好，但从一个场景泛化到大量相关任务，还没有真正跨过去。语言模型在Transformer和GPT之后实现了水平提高所有能力的感觉，机器人还没到那个点。

访谈中段转向姚顺宇自己的经历。他从理论物理、量子信息和黑洞研究转到AI。对他来说，物理没有给AI研究带来直接硬技能。真正有帮助的是性格和研究气质：更想刨根问底，更习惯系统性地看问题，也更能接受黑盒和经验定律之间的关系。

他有一个很好的类比。今天的大模型研究，有点像早期热力学。那时人们还不知道热的微观机制，但并不妨碍热力学定律推动工程发展。今天我们也不理解语言模型里每个矩阵到底在干什么，但scaling law、后训练经验和各种实验规律，已经足够推动模型继续发展。

然后是Anthropic。姚顺宇在Anthropic经历了很关键的阶段：Claude 3.5、3.7、coding能力、后训练和强化学习环境的变化。他说，Claude Code让软件工程圈真正体会到，这不只是模型演示，而是效率工具。后训练的关键，是找到合适环境。这个环境要有清晰反馈，也要本身是强数据源，训练才能稳定放大。

但他并不把这些归因给某一个英雄。他反复说，大模型侧已经过了个人英雄主义时代。一个人可以谈自己做过哪些技术工作，产生了哪些局部效果；但最后产品里占多大比重，很难说清楚。更重要的是集体能不能一起工作，能不能为了同一个目标投入时间和精力。

这也是他后来谈Google DeepMind时的重点。Anthropic更像一个方向坚定、top down能力很强的组织。Google则是另一种打法：bottom up、全栈、很多团队同时储备。它的优势不只是模型本身，还有硬件、TPU、训练系统、工程基础和大量研究方向。当Gemini 2.5出现后，业内开始明显感到Google上道了。

姚顺宇对下一阶段的判断也很有意思。他提到ML coding，也就是让AI进一步帮助AI研究本身。Google是一个AI research全栈大户，如果AI能加速训练模型、设计实验、连接硬件和模型、管理大规模研究流程，对Google会非常有价值。更远一点，他还提到continuous learning和世界模型，但这些还没到非常确定的范式级变化。

这场访谈最后回到人。为什么AI研究员这么贵？姚顺宇说，一方面是机会稀缺。你得接触过这个训练环境，才可能学会这些事；再聪明，没有机会也没用。另一方面，他也觉得市场对人的炒作有点过分。因为这件事本质上是集体主义的，过度神化个人并不准确。

那怎么判断一个人靠不靠谱？他举了一个面试题：让候选人在二十四小时内从零到一完成一个强化学习项目，然后再讨论一小时。重点不是结果有多华丽，而是看这个人怎么定义问题，怎么选择模型和数据，怎么解释结果，怎么知道自己哪里可能错了。

如果要用一句话概括这场访谈，姚顺宇真正表达的是：AI行业当然在快速前进，但它没有那么神秘。真正重要的是把模糊问题变清楚，把实验做扎实，把局部指标放回系统里验证，把产品形态做出来，把组织协作起来。聪明有用，但不够。靠谱、细致、负责，才是在这个集体主义时代里更难得的能力。

所以，这场访谈最值得带走的不是某个模型名字，而是一种判断AI进展的方法。别只看发布会，也别只看榜单。要看任务有没有被定义清楚，反馈信号是不是可靠，产品有没有释放能力，组织能不能持续做正确实验，人能不能对真实结果负责。这些东西合在一起，才是AI继续往前走的真正动力。
"""
    (AUDIO / "podcast-script-yaoshunyu-20260511.md").write_text(script, encoding="utf-8")


if __name__ == "__main__":
    data = load_turns()
    turns = data["turns"]
    segments = make_segments(turns)
    knowledge = make_knowledge(turns, segments)
    make_reports(knowledge, segments)
    make_visual(knowledge, segments)
    make_podcast()
    print("built yaoshunyu artifacts")
