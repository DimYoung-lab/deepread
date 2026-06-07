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


def quote(turns_by_time, timestamp, max_chars=160):
    text = turns_by_time[timestamp]["text"].strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    for mark in "。！？":
        pos = cut.rfind(mark)
        if pos >= 30:
            return cut[: pos + 1]
    return cut.rstrip() + "..."


def make_segments(turns):
    bounds = [
        (0, 698, "开场：人类像小模型，AI要成为生产工具", "李想把人类和 AI 的关系放在第一层讨论：人类不擅长处理超大规模信息，AI 的价值不应停在信息工具，而要真正进入行动和生产。"),
        (698, 1425, "DeepSeek与人类最佳实践", "李想从 DeepSeek 身上提炼出研究、研发、能力表达、业务价值四步法，并把它映射到组织协作和理想自身的能力建设。"),
        (1425, 2074, "春节冲击：开源、基座模型与理想同学", "DeepSeek 爆火迫使理想重新评估自研基座模型和理想同学路径：既拥抱开源，也继续投入自己的专业模型能力。"),
        (2074, 3158, "VLA：把智能驾驶做成司机大模型", "访谈进入技术核心：李想解释 VLA 如何从视觉、语言、行动三个维度把自动驾驶从辅助工具推向生产工具。"),
        (3158, 4250, "专业 Agent、端到端与VLA落地", "李想强调端到端不是被抛弃，而是成为 VLA 的行动部分；真正的 Agent 需要在专业场景里调用工具、执行动作并承担结果。"),
        (4250, 5033, "安全、终局架构与智驾原创性", "围绕 VLA 的安全、下一代架构和原创性，李想把理想的优势归结为研究、编译、芯片、操作系统和真实车队数据的长期积累。"),
        (5033, 6010, "雁栖湖战略：理想是谁", "战略讨论从销量转向身份：理想要成为人工智能终端公司，而不是只在汽车行业里做一个更大的车企。"),
        (6010, 6512, "AGI终端的边界：车、眼镜、机器人与规模", "李想给出 AGI 时代终端的四个标准，并说明理想会随规模扩大进入新的终端形态，但不会为了概念而分散。"),
        (6512, 7662, "组织转型：能量、人才密度与CEO学习", "这一段讨论理想如何从制造业文化转向 AI 企业文化，以及李想如何通过学习、战略会和人才密度重塑组织。"),
        (7662, 8606, "十年记忆、成长与亲密关系", "访谈从公司转到个人：李想回顾创业十年的幸福与痛苦，并把能量来源归结为关注自己、关注他人和稳定的亲密关系。"),
        (8606, 9220, "世界观：AI应服务人，而不是让人更疲劳", "李想把智慧定义为人与万物的关系，认为 AI 的意义是释放人去做更有价值、更有能量的事。"),
        (9220, 10**9, "智慧、群体增强与认知主权", "最后的讨论落在人类如何面对更强的 AI：李想更关心关系、智慧和群体增强，而不是单纯追逐智能强度。"),
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
    turns_by_time = {t["timestamp_raw"]: t for t in turns}
    q = lambda ts, n=155: {"text": quote(turns_by_time, ts, n), "timestamp": ts, "speaker": "李想"}

    segment_payloads = [
        {
            "id": "seg_01",
            "title": segments[0]["title"],
            "summary": segments[0]["summary"],
            "topics": ["AI工具分层", "生产工具", "人类与模型的差异"],
            "insights": [
                {"claim": "AI如果只提供答案，仍然只是信息工具；只有能行动并替代专业工作，才真正产生生产力。", "explanation": "李想把 AI 分成信息工具、辅助工具和生产工具三层，并把 Agent 的核心标准定义为是否能处理工作中最重要的八小时。", "type": "分析框架", "source_timestamp": "06:52", "confidence": "high"},
                {"claim": "专业 Agent 的关键不是更会聊天，而是能知行合一。", "explanation": "他反复强调 action：控制电脑、车辆或工具，才会把策略转化成价值。", "type": "因果论断", "source_timestamp": "09:11", "confidence": "high"},
            ],
            "quotes": [q("01:01"), q("06:52", 210), q("09:11", 180)],
            "data_points": [{"label": "上下文窗口", "value": "主持人提到 Google 和 OpenAI 已支持 100 万 token 级上下文", "timestamp": "00:44"}],
            "contradictions": [{"tension": "AI越普及，很多人的工作时间并没有减少，反而更卷。", "timestamp": "04:05"}],
            "predictions": [{"prediction": "下一阶段的 Agent 评价标准会从聪明程度转向是否能成为生产工具。", "time_horizon": "接下来一阶段", "confidence": "high", "timestamp": "06:52"}],
        },
        {
            "id": "seg_02",
            "title": segments[1]["title"],
            "summary": segments[1]["summary"],
            "topics": ["DeepSeek", "人类最佳实践", "组织方法论"],
            "insights": [
                {"claim": "DeepSeek最值得学的不是流量，而是极简地执行了人类最佳实践。", "explanation": "李想总结为研究、研发、能力表达、业务价值四步，并认为组织经常跳过研究或复盘。", "type": "心智模型", "source_timestamp": "13:52", "confidence": "high"},
                {"claim": "卓越组织要反人性，因为严格遵守最佳实践往往不符合随心所欲的本能。", "explanation": "他把组织能力的难点放在对抗惯性：不急着改策略，而是先复盘、分析、确定目标。", "type": "反直觉洞察", "source_timestamp": "18:18", "confidence": "high"},
            ],
            "quotes": [q("13:52", 180), q("18:18", 220), q("21:56", 190)],
            "data_points": [{"label": "开源节省时间", "value": "DeepSeek 开源让理想 VLA 语言模型部分缩短约九个月", "timestamp": "21:56"}],
            "contradictions": [{"tension": "组织想快速推进业务，但真正的能力建设需要先研究再研发。", "timestamp": "18:18"}],
            "predictions": [{"prediction": "能把最佳实践内化为组织流程的公司，会在 AI 能力建设中取得更高研发效率。", "time_horizon": "持续", "confidence": "medium", "timestamp": "20:10"}],
        },
        {
            "id": "seg_03",
            "title": segments[2]["title"],
            "summary": segments[2]["summary"],
            "topics": ["DeepSeek流量", "基座模型", "理想同学"],
            "insights": [
                {"claim": "DeepSeek没有把所有算力用在流量上，是因为能力提升比短期用户量更重要。", "explanation": "李想认为 query 有价值，但过量推理会挤占训练资源。", "type": "因果论断", "source_timestamp": "24:04", "confidence": "high"},
                {"claim": "理想既要拥抱开源，也不能放弃专业基座模型投入。", "explanation": "原因是 VLA、理想同学和端侧智能都需要面向物理世界和专业任务的模型能力。", "type": "分析框架", "source_timestamp": "26:14", "confidence": "high"},
            ],
            "quotes": [q("24:04", 180), q("26:14", 210), q("31:39", 170)],
            "data_points": [{"label": "时间窗口", "value": "主持人提到距离上次 AI Talk 过去 130 天", "timestamp": "02:33"}],
            "contradictions": [{"tension": "开源模型很强，但理想仍然需要自建专业模型和端侧能力。", "timestamp": "31:23"}],
            "predictions": [{"prediction": "理想同学会从 App/语音助手继续向更完整的 AI 终端入口演进。", "time_horizon": "2025年以后", "confidence": "medium", "timestamp": "32:41"}],
        },
        {
            "id": "seg_04",
            "title": segments[3]["title"],
            "summary": segments[3]["summary"],
            "topics": ["VLA", "智能驾驶", "司机大模型"],
            "insights": [
                {"claim": "VLA不是突变，而是智能驾驶从昆虫智能、哺乳动物智能到人类司机智能的进化。", "explanation": "李想用三阶段类比解释技术路线：规则和感知像昆虫，端到端加 VLM 像哺乳动物，VLA 才开始理解物理世界并行动。", "type": "类比", "source_timestamp": "36:38", "confidence": "high"},
                {"claim": "VLA的价值在于把车从辅助驾驶推向生产力工具。", "explanation": "它不仅看见世界，还理解世界、推理并执行行动，最终像司机一样沟通和处理复杂问题。", "type": "因果论断", "source_timestamp": "47:18", "confidence": "high"},
            ],
            "quotes": [q("35:25", 180), q("39:01", 200), q("47:18", 220)],
            "data_points": [
                {"label": "端侧模型", "value": "VLA 端侧蒸馏模型约 3.2B，八个专家组成 MOE", "timestamp": "42:14"},
                {"label": "COT长度", "value": "交通场景中 COT 通常控制在 2-3 步以降低延时", "timestamp": "43:58"},
            ],
            "contradictions": [{"tension": "智能驾驶被质疑时，李想反而认为这是理想解决行业难题的机会。", "timestamp": "35:25"}],
            "predictions": [{"prediction": "专业司机 Agent 会比通用 Agent 更早在自动驾驶中产生生产力。", "time_horizon": "近期产品化", "confidence": "high", "timestamp": "50:39"}],
        },
        {
            "id": "seg_05",
            "title": segments[4]["title"],
            "summary": segments[4]["summary"],
            "topics": ["专业Agent", "Agent OS", "端到端"],
            "insights": [
                {"claim": "端到端没有被放弃，它成为 VLA 的行动部分。", "explanation": "李想把端到端视为具身智能执行环节，VLA 在其上增加语言、3D vision 和高清 2D vision。", "type": "澄清", "source_timestamp": "56:12", "confidence": "high"},
                {"claim": "公司内部的 Agent 应由专业团队开发，平台团队提供 Agent OS。", "explanation": "客服、销售、编程等场景各自需要专业数据、工具和思维链，不能指望一个通用团队替所有人做好。", "type": "组织设计", "source_timestamp": "54:29", "confidence": "high"},
            ],
            "quotes": [q("52:43", 180), q("54:29", 220), q("56:12", 160)],
            "data_points": [{"label": "芯片适配", "value": "理想称可在双 Orin X 与 Thor-U 上运行同等规模 VLA 模型", "timestamp": "59:10"}],
            "contradictions": [{"tension": "外界期待一步到位，但李想反复强调没有捷径，基本功无法跳过。", "timestamp": "57:06"}],
            "predictions": [{"prediction": "企业内 Agent 会先在客服、销售、编程、实验验证等高频专业工作中落地。", "time_horizon": "公司内部推进", "confidence": "high", "timestamp": "53:57"}],
        },
        {
            "id": "seg_06",
            "title": segments[5]["title"],
            "summary": segments[5]["summary"],
            "topics": ["VLA安全", "原创性", "基础能力"],
            "insights": [
                {"claim": "VLA安全不是靠口号，而是在强化学习、人类反馈和社会驾驶习惯对齐中完成。", "explanation": "李想把安全对齐放在后训练和强化阶段，强调要开得像社会中的成熟司机，而不是新手。", "type": "因果论断", "source_timestamp": "45:18", "confidence": "high"},
                {"claim": "理想的原创性来自长期基础能力堆叠，而不是突然押中一条路线。", "explanation": "他列举编译、芯片、操作系统、世界模型和真实车队数据，说明 VLA 是多年研究的结果。", "type": "分析框架", "source_timestamp": "59:10", "confidence": "high"},
            ],
            "quotes": [q("45:18", 170), q("59:10", 190), q("01:03:21", 170)],
            "data_points": [{"label": "DeepSeek帮助", "value": "李想称 DeepSeek 可帮助 VLA 缩短约九个月", "timestamp": "01:03:21"}],
            "contradictions": [{"tension": "VLA被视为新路线，但李想强调它建立在端到端、VLM和底层工程之上。", "timestamp": "56:12"}],
            "predictions": [{"prediction": "VLA会继续演进，但真正困难的是完整系统工程和安全对齐。", "time_horizon": "未来一年及以后", "confidence": "medium", "timestamp": "01:12:55"}],
        },
        {
            "id": "seg_07",
            "title": segments[6]["title"],
            "summary": segments[6]["summary"],
            "topics": ["AI终端公司", "雁栖湖战略", "苹果/安卓类比"],
            "insights": [
                {"claim": "理想的新身份不是车企加 AI，而是人工智能终端公司。", "explanation": "李想用 PC、移动互联网和 AI 时代的终端类比，说明 action 需要终端承载。", "type": "战略判断", "source_timestamp": "01:34:32", "confidence": "high"},
                {"claim": "AGI时代终端必须有感知、认知决策、行动和反思反馈四个能力。", "explanation": "这是李想判断车、眼镜、机器人等终端是否值得做的核心标准。", "type": "分析框架", "source_timestamp": "01:27:06", "confidence": "high"},
            ],
            "quotes": [q("01:27:06", 220), q("01:34:32", 200), q("01:47:16", 180)],
            "data_points": [
                {"label": "规模目标", "value": "李想提到汽车可能成为 AI 时代千亿美金收入级终端", "timestamp": "01:26:26"},
                {"label": "组织规模假设", "value": "若 5万-10万人做到1000亿美金收入，才证明 AI 战略真正发挥价值", "timestamp": "01:44:48"},
            ],
            "contradictions": [{"tension": "资本市场仍按销量评估，但李想希望用 L4 和组织效率证明 AI 终端战略。", "timestamp": "01:44:48"}],
            "predictions": [{"prediction": "到2030年前后，车之外还会出现符合 AGI 终端四要素的新形态。", "time_horizon": "3-6年/到2030年", "confidence": "medium", "timestamp": "01:28:07"}],
        },
        {
            "id": "seg_08",
            "title": segments[7]["title"],
            "summary": segments[7]["summary"],
            "topics": ["机器人", "穿戴终端", "规模边界"],
            "insights": [
                {"claim": "理想不会为概念做终端，进入新终端取决于规模、用户需求和技术成熟度。", "explanation": "李想承认眼镜、家庭机器人都有可能，但现阶段显示、计算、电池、路线都未成熟。", "type": "边界判断", "source_timestamp": "01:41:52", "confidence": "high"},
                {"claim": "制造业里的 AGI 不应只盯着替代人，而应重构生产效率。", "explanation": "他把工厂视为可能被 AGI 改造成一个更高效的“机器人系统”。", "type": "反直觉洞察", "source_timestamp": "01:39:04", "confidence": "high"},
            ],
            "quotes": [q("01:39:04", 190), q("01:41:52", 170), q("01:43:32", 180)],
            "data_points": [{"label": "终端判断", "value": "穿戴机器人、空间机器人、家庭机器人都处在研究和路线判断阶段", "timestamp": "01:41:42"}],
            "contradictions": [{"tension": "扩张是规模企业的必然，但过早扩张会破坏收敛。", "timestamp": "01:43:32"}],
            "predictions": [{"prediction": "家庭机器人可能不是单一人形路线，也可能是统一感知和大脑加专用设备。", "time_horizon": "未来路线探索", "confidence": "medium", "timestamp": "01:42:27"}],
        },
        {
            "id": "seg_09",
            "title": segments[8]["title"],
            "summary": segments[8]["summary"],
            "topics": ["组织文化", "人才密度", "CEO成长"],
            "insights": [
                {"claim": "AI转型不是把汽车业务放下，而是把 CEO 和组织的大部分注意力转向新能力。", "explanation": "李想承认自己大量时间在 AI 上，但仍以基本功、用户价值和组织能力作为转型尺度。", "type": "组织判断", "source_timestamp": "01:54:32", "confidence": "high"},
                {"claim": "人才竞争的关键不是复制年轻团队，而是提高人才密度并让不同能力形成合力。", "explanation": "他把组织看作多个大脑和心脏的组合，需要能量凝结而不是内耗。", "type": "心智模型", "source_timestamp": "01:52:21", "confidence": "medium"},
            ],
            "quotes": [q("01:47:56", 170), q("01:54:40", 180), q("02:04:04", 130)],
            "data_points": [{"label": "时间投入", "value": "主持人提到李想可能把十分之八甚至十分之九时间投入 AI", "timestamp": "01:54:32"}],
            "contradictions": [{"tension": "理想需要 AI 企业文化，但仍要保持汽车制造业的质量、交付和基本功。", "timestamp": "01:55:22"}],
            "predictions": [{"prediction": "AI 企业的组织形态会倒逼传统制造组织提高人才密度和研究能力。", "time_horizon": "持续转型", "confidence": "medium", "timestamp": "01:57:02"}],
        },
        {
            "id": "seg_10",
            "title": segments[9]["title"],
            "summary": segments[9]["summary"],
            "topics": ["十年创业", "能量", "亲密关系"],
            "insights": [
                {"claim": "李想认为自己没有变，变化的是问题规模、用户规模和组织规模。", "explanation": "他把高中时代站长经验和今天的 CEO 状态连在一起：解决别人不愿解决的问题。", "type": "自我认知", "source_timestamp": "02:11:15", "confidence": "high"},
                {"claim": "能量来自关注人：先接受自己，再看见他人的优点、互补和成长。", "explanation": "这套关于人和亲密关系的理解，被他同时用于家庭和公司组织。", "type": "心智模型", "source_timestamp": "02:12:46", "confidence": "high"},
            ],
            "quotes": [q("02:11:15", 190), q("02:12:46", 180), q("02:15:57", 170)],
            "data_points": [{"label": "十周年", "value": "主持人提到 7 月是理想十周年", "timestamp": "02:07:42"}],
            "contradictions": [{"tension": "创业叙事常强调苦，李想更愿意从幸福和能量侧理解十年。", "timestamp": "02:10:47"}],
            "predictions": [{"prediction": "组织的持续能量来自稳定亲密关系和互补能力，而不是单个强人。", "time_horizon": "长期", "confidence": "medium", "timestamp": "02:15:57"}],
        },
        {
            "id": "seg_11",
            "title": segments[10]["title"],
            "summary": segments[10]["summary"],
            "topics": ["世界观", "AI服务人", "智慧"],
            "insights": [
                {"claim": "智慧不是更聪明，而是处理人与万物关系的能力。", "explanation": "李想把智慧放在关系和时间里理解：要有足够时间接触人和世界，才会形成真实关系。", "type": "定义", "source_timestamp": "02:25:21", "confidence": "high"},
                {"claim": "AI服务谁取决于人类；它可以是生产工具，也可以是作恶工具。", "explanation": "他认为现阶段至少很长时间内，AI 的方向仍由人类决定。", "type": "因果论断", "source_timestamp": "02:27:40", "confidence": "high"},
            ],
            "quotes": [q("02:25:21", 190), q("02:26:42", 190), q("02:27:40", 180)],
            "data_points": [{"label": "效率目标", "value": "李想举例希望邀约电话由 agent 完成，节省销售人员 20%-30% 时间", "timestamp": "02:26:42"}],
            "contradictions": [{"tension": "AI本应减少疲劳，但当前很多应用反而让人更疲劳。", "timestamp": "02:29:22"}],
            "predictions": [{"prediction": "真正有意义的 AI 会把低价值消耗性工作交给 Agent，让人回到高价值关系和创造。", "time_horizon": "近期业务目标", "confidence": "high", "timestamp": "02:26:42"}],
        },
        {
            "id": "seg_12",
            "title": segments[11]["title"],
            "summary": segments[11]["summary"],
            "topics": ["AI安全", "群体智慧", "认知主权"],
            "insights": [
                {"claim": "当前大模型架构对人类相对安全，因为信息、财产和人身安全仍可通过人类对齐处理。", "explanation": "李想承认未来架构若突破可能带来新问题，但认为今天的担忧很多是过虑。", "type": "判断", "source_timestamp": "02:30:06", "confidence": "medium"},
                {"claim": "提升人类智慧可能要从关系教育和对话训练开始，而不只是提升智力。", "explanation": "他把孩子、校招、希腊哲学式对话连在一起，提出智慧可以被启发和训练。", "type": "教育观", "source_timestamp": "02:35:50", "confidence": "medium"},
            ],
            "quotes": [q("02:30:06", 180), q("02:35:50", 180), q("02:39:31", 170)],
            "data_points": [{"label": "亲密关系上限", "value": "李想认为亲密关系没有固定人数，但应限于家人、少数朋友和共同扛责任的人", "timestamp": "02:39:31"}],
            "contradictions": [{"tension": "AI智能可快速增强，但人类智慧和关系能力未必同步提高。", "timestamp": "02:36:37"}],
            "predictions": [{"prediction": "面对更强 AI，人类需要保留并强化关系、智慧和对价值的判断。", "time_horizon": "长期", "confidence": "medium", "timestamp": "02:40:10"}],
        },
    ]

    themes = [
        {"id": "theme_1", "name": "从聪明到行动", "description": "AI的关键跃迁不是回答更漂亮，而是能够进入行动、调用工具并承担生产结果。", "appears_in_segments": ["seg_01", "seg_04", "seg_05", "seg_11"]},
        {"id": "theme_2", "name": "专业Agent优于通用幻想", "description": "李想反复强调医生、律师、司机、客服等专业场景需要不同数据、工具和思维链。", "appears_in_segments": ["seg_01", "seg_04", "seg_05"]},
        {"id": "theme_3", "name": "研究先于研发", "description": "DeepSeek给理想的启发，是把研究、研发、能力表达和业务价值重新排成能力建设流程。", "appears_in_segments": ["seg_02", "seg_06", "seg_09"]},
        {"id": "theme_4", "name": "AI终端公司的身份重写", "description": "理想的战略叙事从车企扩展为AI时代的终端公司，车只是第一个高收入、高行动密度的终端。", "appears_in_segments": ["seg_07", "seg_08"]},
        {"id": "theme_5", "name": "基本功没有捷径", "description": "无论是VLA还是组织转型，李想都把长期基础能力视为不可跳过的门槛。", "appears_in_segments": ["seg_04", "seg_05", "seg_06", "seg_07"]},
        {"id": "theme_6", "name": "组织是更完整的大脑", "description": "理想的组织观不是单点英雄，而是多个互补的人形成更强大脑、心脏和能量。", "appears_in_segments": ["seg_02", "seg_09", "seg_10", "seg_12"]},
        {"id": "theme_7", "name": "智慧来自关系", "description": "访谈后段把AI、家庭、教育和世界观串起来：智能解决问题，智慧处理关系。", "appears_in_segments": ["seg_10", "seg_11", "seg_12"]},
    ]
    all_quotes = [qt for seg in segment_payloads for qt in seg["quotes"]]
    metadata = {
        "title": "对李想的第二次3小时访谈：CEO大模型、VLA与AI终端公司",
        "date": "2025-10-30",
        "guest": {"name": "李想", "affiliation": "理想汽车创始人兼CEO"},
        "interviewer": {"name": "张小珺"},
        "source": "lixiang.docx",
        "duration": {"total_seconds": 9807, "formatted": "2小时43分钟27秒"},
        "total_duration_seconds": 9807,
        "total_turns": 483,
        "language": "zh",
    }
    knowledge = {
        "metadata": metadata,
        "segments": segment_payloads,
        "cross_cutting_themes": themes,
        "open_questions": [
            {"question": "理想能否在保持汽车基本盘的同时完成AI终端公司转型？", "related_segments": ["seg_07", "seg_08", "seg_09"]},
            {"question": "VLA能否真正从辅助工具跨越到生产工具，并在安全上被大规模验证？", "related_segments": ["seg_04", "seg_05", "seg_06"]},
            {"question": "AI释放人的时间后，人类是否真的会把时间用于更高质量的关系和智慧？", "related_segments": ["seg_11", "seg_12"]},
        ],
    }
    DATA.joinpath("knowledge.json").write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")
    return knowledge, all_quotes


def make_reports(knowledge):
    meta = knowledge["metadata"]
    segments = knowledge["segments"]
    themes = knowledge["cross_cutting_themes"]
    q = [qt for s in segments for qt in s["quotes"]]

    tldr = f"""# 李想 × 未尽之约：速览

*嘉宾：李想，理想汽车创始人兼CEO｜时长：2小时43分钟｜日期：2025-10-30*

## 核心观点

1. **李想把 AI 的分水岭定义为“能不能行动”。** 在他看来，只会回答问题的 AI 仍是信息工具；能调用工具、控制软件或机器、替代专业工作，才是生产工具。
2. **理想的新战略不是“车企加 AI”，而是“人工智能终端公司”。** 汽车被视为第一个高价值 AI 终端，因为它具备感知、决策、行动和反馈闭环。
3. **VLA 是理想把自动驾驶推向司机 Agent 的核心路线。** 李想认为端到端没有被抛弃，而是成为 VLA 的 action 部分，语言和视觉能力会让车更像人类司机。
4. **DeepSeek 对理想最大的启发不是流量，而是最佳实践。** 李想反复强调研究、研发、能力表达、业务价值四步法，并把它迁移到组织管理。
5. **通用 Agent 不是短期答案，专业 Agent 才更可能先产生生产力。** 司机、医生、律师、客服、编程等场景需要不同数据、工具和思维链。
6. **访谈后段真正的底层主题是“智慧来自关系”。** 李想把家庭、组织和 AI 连接到同一个问题：技术应让人有更多时间处理人与世界的关系。

## 最令人意外的洞察

最意外的是，李想并没有把 AI 的终局讲成“模型越来越强”，而是讲成“人能不能从低价值消耗中被释放出来”。他对 Agent 的判断很朴素：如果销售仍要把大量时间花在邀约电话上，人工智能就没有真正产生意义。这个标准比行业常见的参数、榜单和演示更苛刻，也更贴近用户。

## 值得引用的金句

> "{q[1]['text']}" — *{q[1]['timestamp']}*

> "{q[2]['text']}" — *{q[2]['timestamp']}*

> "{q[10]['text']}" — *{q[10]['timestamp']}*

> "{q[31]['text']}" — *{q[31]['timestamp']}*

## 适合谁读

适合关注 AI 产品落地、智能汽车、企业战略转型和组织管理的读者，尤其适合正在判断“AI到底怎样才算有生产力”的创业者、产品经理和管理者。

## 阅读指南

如果只关心 AI 产品判断，优先读“从人类小模型到AI生产工具”和“专业 Agent、端到端与VLA落地”。如果关心理想战略，读“雁栖湖战略：理想是谁”和“AGI终端的边界”。如果关心李想本人，读最后三段关于能量、家庭、智慧和关系的部分。
"""

    report_parts = [
        "# 李想 × 未尽之约：深度报告",
        "",
        "*嘉宾：李想，理想汽车创始人兼CEO｜主持：张小珺｜时长：2小时43分钟｜日期：2025-10-30｜来源：lixiang.docx*",
        "",
        "## 访谈概览",
        "",
        "### 嘉宾简介",
        "李想是理想汽车创始人兼 CEO，也是中国新造车公司中少数持续把产品、组织、技术和战略放在同一张图里讨论的创业者。本次访谈里，他不只谈车，而是试图回答理想为什么要成为一家人工智能终端公司。",
        "",
        "### 访谈背景",
        "这是张小珺对李想的第二次长访谈，时间点位于 DeepSeek 爆火、理想重新组织 AI 战略、VLA 技术路线逐渐清晰之后。访谈从 AI 工具价值开始，进入自动驾驶、AGI 终端、组织转型，最后落到家庭、智慧与人类关系。",
        "",
        "### 关键数据",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 覆盖话题数 | {len(segments)} |",
        f"| 提取金句数 | {sum(len(s['quotes']) for s in segments)} |",
        f"| 重要预测数 | {sum(len(s['predictions']) for s in segments)} |",
        "| 对话轮次 | 483 |",
        "",
        "## 执行摘要",
        "",
        "这场访谈的核心不是“理想要不要做 AI”，而是李想如何重新定义 AI 的商业价值：只有能行动、能调用工具、能替代专业工作并承担结果的 AI，才配叫生产工具。这个判断贯穿了他对 Agent、VLA、理想同学、AGI 终端和公司组织的全部解释。",
        "",
        "围绕这一点，他搭出三条主线。第一，DeepSeek 让他重新强调人类最佳实践：研究、研发、能力表达、业务价值，组织如果跳过研究和复盘，就会忙而无效。第二，VLA 是理想在智能驾驶上押注的司机大模型路线，它把端到端、VLM、语言模型和 action 合成一个能在物理世界工作的系统。第三，理想的战略身份正在从“家庭 SUV 公司”变成“人工智能终端公司”，车只是第一个具备感知、认知、行动和反馈闭环的大型终端。",
        "",
        "访谈后半段让这个战略有了人的底色。李想反复谈“能量”“成长”“亲密关系”和“智慧”，不是偏题，而是在说明他理解的 AI 价值：技术应该减少人的低价值消耗，让人有更多时间处理人与人、人与世界的关系。如果 AI 只是让人更卷，它就还没有抵达他定义中的生产工具阶段。",
        "",
        "## 阅读指南",
        "",
        "| 读者类型 | 推荐阅读 | 预计时间 |",
        "|---|---|---|",
        "| 管理者 / 决策者 | 执行摘要、跨领域主题、预测总结 | 8 分钟 |",
        "| AI 产品从业者 | 话题 1、3、5、11 | 20 分钟 |",
        "| 智能汽车从业者 | 话题 4、5、6、7 | 25 分钟 |",
        "| 关注李想个人变化的读者 | 话题 9、10、11、12 | 15 分钟 |",
        "",
        "## 话题深度分析",
        "",
    ]
    for seg in segments:
        report_parts += [
            f"### {seg['title']} *({next(s for s in make_segments(load_turns()['turns']) if s['id']==seg['id'])['time_range']})*",
            "",
            "#### 背景",
            seg["summary"],
            "",
            "#### 核心论点",
        ]
        for ins in seg["insights"]:
            report_parts.append(f"{ins['claim']} {ins['explanation']}（{ins['source_timestamp']}）")
            report_parts.append("")
        for qt in seg["quotes"][:2]:
            report_parts += [f"> **核心引述** *({qt['timestamp']})*:", f"> \"{qt['text']}\"", ""]
        if seg["data_points"]:
            report_parts.append("> **数据点：**")
            for dp in seg["data_points"]:
                report_parts.append(f"> - **{dp['label']}**：{dp['value']}（{dp['timestamp']}）")
            report_parts.append("")
    report_parts += [
        "## 跨领域主题",
        "",
    ]
    for theme in themes:
        report_parts += [
            f"### {theme['name']}",
            "",
            theme["description"],
            "",
            "**跨话题例证:**",
        ]
        for sid in theme["appears_in_segments"][:3]:
            seg = next(s for s in segments if s["id"] == sid)
            report_parts.append(f"- 从 **{seg['title']}**：{seg['insights'][0]['claim']}（{seg['insights'][0]['source_timestamp']}）")
        report_parts.append("")
    report_parts += [
        "## 矛盾与未解问题",
        "",
        "| # | 张力 / 问题 | 出现场景 | 处理状态 |",
        "|---|---|---|---|",
        "| 1 | AI被大量使用但工作时长并未减少 | 00:04:05 | 未完全解决，李想用生产工具标准回应 |",
        "| 2 | 理想既要做车企基本盘，又要做AI终端公司 | 01:44:48 | 以L4和组织效率作为未来验证 |",
        "| 3 | 通用模型能力很强，但专业场景仍需自建模型 | 00:31:23 | 通过开源+自研专业能力并行处理 |",
        "| 4 | AI智能增强快于人类智慧增强 | 02:36:37 | 嘉宾转向关系教育和群体智慧 |",
        "",
        "## 预测总结",
        "",
        "| # | 预测 | 时间窗口 | 置信度 | 条件 / 限制 |",
        "|---|---|---|---|---|",
        "| 1 | 专业 Agent 会比通用 Agent 更早产生生产力 | 近期 | 高 | 必须有专业数据、工具、action和责任闭环 |",
        "| 2 | VLA会推动智能驾驶从辅助工具走向生产工具 | 未来一年及以后 | 中高 | 取决于安全对齐、端侧性能和真实场景验证 |",
        "| 3 | 车之外会出现新的AGI终端形态 | 3-6年/到2030年 | 中 | 取决于感知、计算、电池、显示和服务运营成熟度 |",
        "| 4 | AI的真正价值会体现在减少低价值消耗性工作 | 近期业务目标 | 高 | 企业必须把Agent放到真实流程里 |",
        "",
        "## 金句全集",
        "",
    ]
    for qt in q[:24]:
        report_parts.append(f"- \"{qt['text']}\" — *{qt['timestamp']}*")

    social = f"""# 李想这场访谈，真正讲的是：AI不该只让人更忙

这场 2 小时 43 分钟的访谈里，李想反复讲一个判断：

AI 的价值不是“回答得更聪明”，而是能不能行动，能不能替代专业工作，能不能真正减少人的低价值消耗。

几个最值得记住的点：

1. AI 分三层：信息工具、辅助工具、生产工具。今天大部分 AI 还停留在信息工具。
2. Agent 的核心不是会聊天，而是 action：能控制电脑、车、软件和真实工具。
3. VLA 是理想把自动驾驶做成“司机大模型”的路径，端到端不是被放弃，而是成为 action 部分。
4. 理想的新身份是“人工智能终端公司”，车只是第一个足够大的 AGI 终端。
5. 李想对 DeepSeek 的理解很特别：他学到的不是流量打法，而是人类最佳实践。
6. 访谈后半段谈家庭、关系和智慧，其实和 AI 主线是连着的：AI 应该释放人的时间，让人处理更有价值的关系。

金句：

> "{q[2]['text']}" — {q[2]['timestamp']}

> "{q[31]['text']}" — {q[31]['timestamp']}

适合关注 AI 产品、智能汽车、组织转型和长期战略的人读。尤其适合正在问“AI到底怎样才算有用”的人。

#李想 #理想汽车 #AI #VLA #Agent #智能驾驶
"""
    (REPORTS / "tldr-lixiang-20251030.md").write_text(tldr, encoding="utf-8")
    (REPORTS / "report-lixiang-20251030.md").write_text("\n".join(report_parts), encoding="utf-8")
    (REPORTS / "social-lixiang-20251030.md").write_text(social, encoding="utf-8")


def make_visual(knowledge):
    meta = knowledge["metadata"]
    segments = knowledge["segments"]
    themes = []
    colors = ["#7f1d1d", "#92400e", "#166534", "#075985", "#5b21b6", "#9f1239", "#334155"]
    for i, theme in enumerate(knowledge["cross_cutting_themes"]):
        related_segments = [s for s in segments if s["id"] in theme["appears_in_segments"]]
        insights = []
        quotes = []
        for seg in related_segments:
            if seg["insights"]:
                ins = seg["insights"][0]
                insights.append({
                    "claim": ins["claim"],
                    "explanation": ins["explanation"],
                    "importance": 5 if len(insights) < 2 else 4,
                    "source_segments": [seg["id"]],
                    "key_quote": seg["quotes"][0],
                    "related_data_points": seg["data_points"][:1],
                })
            quotes.extend(seg["quotes"][:1])
        themes.append({
            "id": theme["id"],
            "name": theme["name"],
            "summary": theme["description"],
            "narrative": f"{theme['description']} 这个主题把访谈中的技术路线、组织能力和人的体验连接起来：李想并不满足于模型演示，而是持续追问它能否进入真实流程、真实终端和真实关系。",
            "importance": i + 1,
            "highlighted_insights": insights[:5],
            "highlighted_quotes": quotes[:3],
            "related_themes": [t["id"] for t in knowledge["cross_cutting_themes"] if t["id"] != theme["id"]][:2],
        })
    visual = {
        "meta": {
            "title": meta["title"],
            "guest": meta["guest"],
            "date": meta["date"],
            "duration": meta["duration"]["formatted"],
            "core_thesis": "AI的价值在于行动：从信息工具走向生产工具",
            "core_thesis_elaboration": "李想把 AI、VLA、理想战略和个人世界观统一到同一个问题：技术是否能进入真实行动，减少人的低价值消耗，并帮助人处理更重要的关系。",
            "key_takeaways": [
                {"claim": "AI必须能行动，才算生产工具。", "elaboration": "只提供建议仍然停留在信息工具层，真正的 Agent 要能控制软件、车辆或工具。"},
                {"claim": "VLA是司机大模型，不只是智驾升级。", "elaboration": "它把视觉、语言和行动合成一个理解物理世界的系统。"},
                {"claim": "理想要成为人工智能终端公司。", "elaboration": "车是第一个大型终端，未来边界取决于感知、决策、行动和反馈能力。"},
                {"claim": "专业 Agent 会先于通用 Agent 落地。", "elaboration": "专业工作需要专业数据、工具、COT和安全责任。"},
                {"claim": "智慧来自关系。", "elaboration": "访谈后段把 AI 的意义落到人能否更好地处理自己、他人和世界的关系。"},
            ],
            "most_surprising_insight": {
                "claim": "AI如果不能减少人的低价值消耗，就还没有真正产生意义。",
                "elaboration": "这比行业常见的模型榜单标准更接近真实用户体验。",
                "source_quote": segments[10]["quotes"][1],
            },
            "stats": {
                "duration_formatted": "2h 43m",
                "segment_count": len(segments),
                "insight_count": sum(len(s["insights"]) for s in segments),
                "quote_count": sum(len(s["quotes"]) for s in segments),
                "prediction_count": sum(len(s["predictions"]) for s in segments),
                "theme_count": len(themes),
            },
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
            for s in segments
        ],
        "curated_quotes": [
            {**qt, "context_note": "访谈核心引述", "belongs_to_theme": "theme_1"}
            for s in segments
            for qt in s["quotes"][:2]
        ][:24],
        "map_data": {
            "central_thesis": "AI要从回答走向行动",
            "theme_nodes": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "color": colors[i % len(colors)],
                    "summary": t["summary"],
                    "arguments": [
                        {
                            "claim": ins["claim"][:48],
                            "importance": ins["importance"],
                            "explanation": ins["explanation"],
                            "insight_type": "分析框架",
                            "evidence": [{"type": "quote", "text": ins["key_quote"]["text"][:100], "full_text": ins["key_quote"]["text"], "timestamp": ins["key_quote"]["timestamp"]}],
                        }
                        for ins in t["highlighted_insights"][:3]
                    ],
                    "predictions": [],
                }
                for i, t in enumerate(themes)
            ],
            "cross_links": [
                {"source": "theme_1.0", "target": "theme_2.0", "relation": "supports"},
                {"source": "theme_3.0", "target": "theme_5.0", "relation": "supports"},
                {"source": "theme_4.0", "target": "theme_1.0", "relation": "extends"},
                {"source": "theme_6.0", "target": "theme_7.0", "relation": "extends"},
            ],
            "stats": {"insight_count": 24, "quote_count": 36, "data_point_count": 12, "prediction_count": 12, "theme_count": 7, "segment_count": 12},
        },
    }
    (DATA / "visual_content.json").write_text(json.dumps(visual, ensure_ascii=False, indent=2), encoding="utf-8")


def make_podcast(knowledge):
    script = """HOST:
如果你没有时间听完这场将近三小时的李想访谈，我建议你抓住一个问题：李想到底为什么突然把理想汽车讲成一家“人工智能终端公司”？

这不是一个简单的品牌口号。整场对话里，他其实在搭一套非常完整的判断：AI 的价值不在于回答得更聪明，而在于能不能行动，能不能进入真实工作，能不能替代那些消耗人时间和能量的专业任务。

HOST:
李想先把 AI 分成三层。第一层是信息工具，就是今天很多聊天机器人做的事：回答问题、整理信息、给建议。第二层是辅助工具，比如车里的语音助手、辅助驾驶，可以让体验更顺，但人还必须在场。第三层才是他真正关心的生产工具。

所谓生产工具，就是它不只是“知”，还必须“行”。它要能控制软件、调用工具、操作车辆，甚至进入物理世界。李想判断 Agent 有没有价值，核心不是它的推理链多漂亮，而是它能不能替代人完成专业工作，能不能减少工作里最重要那八小时的消耗。

HOST:
这就解释了为什么他会花很大篇幅讲 VLA。对李想来说，VLA 不只是自动驾驶的新架构，而是“司机大模型”。过去的规则算法像昆虫智能，端到端加 VLM 像哺乳动物智能，而 VLA 要更接近人类司机：看见物理世界，理解导航和道路，做短链条推理，然后执行动作。

他特别强调，端到端没有被放弃，而是变成了 VLA 的 action 部分。也就是说，理想不是把旧路线推倒重来，而是把视觉、语言、行动、安全对齐和端侧运行能力重新组合成一个更完整的司机 Agent。

HOST:
这里还有一个很重要的战略判断：李想不相信短期内会有一个万能通用 Agent 解决所有问题。他更相信专业 Agent。司机、医生、律师、客服、销售、程序员，每个专业都有自己的数据、工具、动作和安全责任。

所以理想内部要做的不是一个神奇的大一统机器人，而是 Agent OS：平台提供模型、工具和训练框架，真正的专业 Agent 由客服团队、销售团队、开发团队自己做出来。

HOST:
DeepSeek 在这场访谈里也很关键。李想学到的不是“怎么接流量”，而是人类最佳实践：先研究，再研发，再把能力表达出来，最后变成业务价值。他说组织最容易犯的错，就是上来直接研发，或者遇到业务问题只改策略，不做复盘、不重新分析、不重新确定目标。

这也是他为什么反复讲“基本功没有捷径”。VLA 不是突然押中路线，而是研究、编译、芯片、操作系统、车队数据、世界模型这些能力堆出来的结果。

HOST:
然后访谈进入最核心的公司战略：理想到底是谁？

李想的回答是，理想要成为人工智能终端公司。车是第一个终端，因为它有 360 度感知，有认知决策，有 action，也有反馈闭环。未来眼镜、家庭机器人、空间机器人都有可能，但他给了一个边界：不符合感知、决策、行动、反馈这四个标准，就不是理想要做的 AGI 终端。

这也是他回应“会不会摊太开”的方式。规模小的时候要收敛，规模大之后必须扩张；但扩张不是追热点，而是围绕用户需求、技术能力和组织能力展开。

HOST:
访谈后半段看起来从 AI 跳到了家庭、关系和智慧，但其实没有跑题。李想真正关心的是：AI 最后到底服务谁？

他的答案很直接：服务谁取决于人类。如果 AI 只是让人更卷，让人工作更久，那它还没有完成使命。真正有意义的 AI，应该把邀约电话、重复沟通、低价值消耗交给 Agent，让销售、产品专家、管理者有更多时间去处理更有价值的事情。

HOST:
所以这场访谈最值得带走的，不是某个技术名词，而是一条判断线：

AI 从信息工具走向生产工具，必须经过 action；公司从车企走向 AI 终端公司，必须经过真实终端；人从更忙走向更有智慧，必须重新处理自己、他人和世界的关系。

如果用一句话概括李想的表达，那就是：智能解决问题，但智慧处理关系。理想要做的 AI，不应该只是更聪明的答案，而应该是让人有更多时间、更少消耗、更多能量的行动系统。
"""
    (AUDIO / "podcast-script-lixiang-20251030.md").write_text(script, encoding="utf-8")


def make_extractions(knowledge):
    for seg in knowledge["segments"]:
        path = SEGMENTS_DIR / f"{seg['id']}_extraction.json"
        payload = {k: seg[k] for k in ["id", "title", "topics", "insights", "quotes", "data_points", "contradictions", "predictions"]}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    data = load_turns()
    turns = data["turns"]
    segments = make_segments(turns)
    knowledge, _ = make_knowledge(turns, segments)
    make_extractions(knowledge)
    make_reports(knowledge)
    make_visual(knowledge)
    make_podcast(knowledge)
    print("built lixiang artifacts")
