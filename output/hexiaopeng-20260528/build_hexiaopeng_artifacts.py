import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
DATA = OUT / "data"
SEGDIR = OUT / "segments"
REPORTS = OUT / "reports"
AUDIO = OUT / "audio"


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_turns():
    return json.loads((DATA / "turns-corrected.json").read_text(encoding="utf-8"))["turns"]


def hms(seconds):
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def quote(text, ts, context, tags=None):
    return {
        "text": text,
        "speaker": "guest",
        "timestamp": ts,
        "context_note": context,
        "tags": tags or [],
        "impact": "high",
    }


segments = [
    {
        "id": "seg_01",
        "title": "AI工具、token与何小鹏skill",
        "time_range": {"start": "00:00:53", "end": "00:10:06"},
        "summary": "Opening survey on AI tools, token metrics, data cost, and whether senior roles can be skillized.",
        "turn_indices": [11, 37],
        "key_topics": ["AI coding", "token指标", "数据成本", "skill化", "CEO能力"],
    },
    {
        "id": "seg_02",
        "title": "从AI汽车到物理AI",
        "time_range": {"start": "00:10:36", "end": "00:21:17"},
        "summary": "Why Xpeng reframes itself as a physical AI company and rejects software-plus-AI patchwork.",
        "turn_indices": [38, 62],
        "key_topics": ["物理AI", "智能电动车", "缝合怪", "上限与下限", "软硬件价值"],
    },
    {
        "id": "seg_03",
        "title": "下注、组织重构与企业AI",
        "time_range": {"start": "00:22:00", "end": "00:39:36"},
        "summary": "The 2025 strategic bet, organization redesign, resistance, and four AI directions.",
        "turn_indices": [63, 105],
        "key_topics": ["战略下注", "组织重构", "愿赌服输", "企业AI", "公理重构"],
    },
    {
        "id": "seg_04",
        "title": "机器人三阶段与人才密度",
        "time_range": {"start": "00:40:27", "end": "00:47:07"},
        "summary": "Robot origin story, team reset, belief shift from no brain to brain-driven design, and talent philosophy.",
        "turn_indices": [106, 127],
        "key_topics": ["机器人三阶段", "大脑驱动", "团队重构", "人才潜力", "商业量产"],
    },
    {
        "id": "seg_05",
        "title": "通用人形机器人的社会入口",
        "time_range": {"start": "00:47:27", "end": "00:57:10"},
        "summary": "Why humanoid form, social acceptance, home entry, public controversy, and the difficulty of robot startups matter.",
        "turn_indices": [128, 157],
        "key_topics": ["通用人形", "情绪价值", "家庭场景", "恐怖谷", "舆论反馈"],
    },
    {
        "id": "seg_06",
        "title": "机器人竞争、运动控制与三条曲线",
        "time_range": {"start": "00:57:46", "end": "01:08:32"},
        "summary": "Robot market structure, why humanoids are hard, motion control, Xpeng's three curves, and robot scale speed.",
        "turn_indices": [158, 188],
        "key_topics": ["机器人市场", "运动控制", "三条曲线", "全球化", "商业量产"],
    },
    {
        "id": "seg_07",
        "title": "G系列高端SUV与跨域融合",
        "time_range": {"start": "01:08:38", "end": "01:16:32"},
        "summary": "How flight-car, robot, chassis, and product capabilities converge into Xpeng's high-end SUV strategy.",
        "turn_indices": [189, 219],
        "key_topics": ["高端SUV", "冗余安全", "线控底盘", "家庭科技", "产品复盘"],
    },
    {
        "id": "seg_08",
        "title": "战略规划、L4与行业终局",
        "time_range": {"start": "01:16:35", "end": "01:25:46"},
        "summary": "CEO time allocation, L4 timing, third-party vs self-research, industry concentration, learning, and regret.",
        "turn_indices": [220, 254],
        "key_topics": ["战略规划", "L4预测", "第三方合作", "行业集中", "实践学习"],
    },
]


extractions = {
    "seg_01": {
        "topics": [
            {"name": "AI工具使用边界", "description": "一号位要看远方, 不能沉没在工具细节里。", "importance": "core", "source_timestamps": ["00:01:40"], "keywords": ["AI coding", "一号位", "远方"]},
            {"name": "物理AI的token指标", "description": "物理世界里关键不是员工token, 而是machine使用算力和数据产生价值。", "importance": "core", "source_timestamps": ["00:04:29", "00:05:57"], "keywords": ["token", "H100", "machine"]},
            {"name": "高级能力skill化", "description": "越高级的蓝白领能力越难验证对错, 也意味着更高层角色长期面临重构。", "importance": "major", "source_timestamps": ["00:08:13", "00:09:27"], "keywords": ["skill", "CEO", "强化"]},
        ],
        "insights": [
            {"claim": "一号位使用AI工具的最佳方式不是深度沉浸, 而是用结果校准方向感。", "explanation": "何小鹏认为天天深度使用工具会把注意力拉到细节, 反而影响远方判断。基层团队应充分试用, 一号位要保留战略视角。", "type": "心智模型", "source_timestamp": "00:01:40", "confidence": "high", "related_insights": []},
            {"claim": "物理AI的核心成本指标不是员工token, 而是数据、算力和机器自用token如何转换成现实价值。", "explanation": "他把数字AI公司的token使用和物理AI训练、运行成本分开看, 认为前者只是很小的数字, 后者才是物理AI的真实约束。", "type": "分析框架", "source_timestamp": "00:04:29", "confidence": "high", "related_insights": []},
            {"claim": "高级角色的skill化难点在于缺少可靠的对错判定和持续强化机制。", "explanation": "何小鹏认为coding和自动驾驶相对容易判断对错, 但CEO式能力的正确性难以定义, 因此不能简单复制现成skill方法。", "type": "因果论断", "source_timestamp": "00:09:27", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("如果他真的有能力花了更多钱，产生更大的价值，为什么你要限制他？", "00:05:19", "Explaining why he avoids blanket token caps.", ["token", "management"]),
            quote("如果把我都能够现在有清晰的逻辑论去skill化，意味着什么？意味着不光是基础的蓝白领，就是更高端的蓝白领上都会有巨大的风险。", "00:08:13", "Discussing what an He Xiaopeng skill would imply.", ["skill", "labor"]),
            quote("比如说把何小鹏skills的话，你很难判断这个skills的话怎么是对的或者是错的，是非常困难的。", "00:09:27", "Explaining the validation problem for senior skillization.", ["skill", "evaluation"]),
        ],
        "data_points": [
            {"value": "物理AI单次训练数据可达几十TB到几百TB。", "type": "statistic", "timestamp": "00:06:35", "is_estimated": True, "context": "Comparing data scale and cost between digital AI and physical AI.", "source_quality": "guest_estimate"},
            {"value": "小鹏一年在数据上的直接刚性成本接近十亿元以上。", "type": "statistic", "timestamp": "00:06:35", "is_estimated": True, "context": "Explaining why data governance matters.", "source_quality": "guest_estimate"},
        ],
        "contradictions": [
            {"statement_a": "团队内部大量使用AI coding。", "timestamp_a": "00:01:21", "statement_b": "何小鹏个人不愿意深度使用。", "timestamp_b": "00:01:40", "resolution_note": "角色不同: 基层强调试用, 一号位强调方向判断。", "type": "qualification"}
        ],
        "predictions": [
            {"prediction": "AI coding可能在2到3年后推动初级程序员升级为高级程序员。", "time_horizon": "2-3年", "confidence": "medium", "conditions": "AI coding工具能力持续提升。", "timestamp": "00:02:50"},
            {"prediction": "数十年或100年后, CEO能力也可能被skill化, 但CEO自身能力结构也会升级。", "time_horizon": "数十年到100年", "confidence": "tentative", "conditions": "高级能力可验证、可强化。", "timestamp": "00:08:36"},
        ],
    },
    "seg_02": {
        "topics": [
            {"name": "汽车企业四种研发能力", "description": "硬件、软件、AI和制造研发共同构成汽车企业基础。", "importance": "major", "source_timestamps": ["00:10:51"], "keywords": ["硬件", "软件", "制造"]},
            {"name": "AI缝合怪与foundation model", "description": "旧路径是软件流程叠加AI工具, 新路径是用更大的模型打开上限再收敛下限。", "importance": "core", "source_timestamps": ["00:13:37", "00:16:19"], "keywords": ["VIA", "foundation model", "缝合怪"]},
            {"name": "数字AI与物理AI分野", "description": "物理世界的数据和约束无法被语言完整概括, 需要同时看上限、下限和广度。", "importance": "core", "source_timestamps": ["00:17:40", "00:19:05"], "keywords": ["物理AI", "下限", "广度"]},
        ],
        "insights": [
            {"claim": "用软件方法论加AI工具只能做出更强的软件, 不能做出真正的物理AI体系。", "explanation": "他把旧自动驾驶路线称作AI缝合怪, 认为其上限不足以到无人驾驶或机器人泛化。", "type": "反直觉洞察", "source_timestamp": "00:16:19", "confidence": "high", "related_insights": []},
            {"claim": "物理AI不是语言问题, 所以不能直接套用数字AI的评估和产品逻辑。", "explanation": "数字AI处理的是高度概括的人类语言, 物理世界每天的数据量无法用语言完整还原, 因此跑分式长板逻辑不足。", "type": "分析框架", "source_timestamp": "00:17:40", "confidence": "high", "related_insights": []},
            {"claim": "物理AI产品必须同时做长板、宽板和短板, 这是CEO下注的真正难点。", "explanation": "物理产品要面对质量、成本、材质、细节、法规等约束, 只做一个长板无法形成商品价值。", "type": "心智模型", "source_timestamp": "00:19:05", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("我把它戏称为叫缝合怪。", "00:12:44", "Describing software rules plus AI algorithms in older autonomy systems.", ["physical AI", "software"]),
            quote("它的上限太低了。", "00:15:04", "Responding to whether the old path is not intelligent enough.", ["autonomy", "ceiling"]),
            quote("数字AI实际上某种角度是用人类的language，物理AI不是用人类language的。", "00:17:40", "Drawing the digital/physical AI distinction.", ["digital AI", "physical AI"]),
            quote("长板跟窄板，窄板要做宽，短板要做长长板要做的更长。", "00:19:05", "Explaining how physical-world competition differs from digital benchmarks.", ["systems", "strategy"]),
        ],
        "data_points": [
            {"value": "小鹏智能电动车前十年完成首款车、量产并卖出第一个10万台。", "type": "event", "timestamp": "00:11:49", "is_estimated": False, "context": "Reviewing the first decade of Xpeng's car business.", "source_quality": "firsthand"},
            {"value": "何小鹏认为未来十年硬件和软件在车或机器人中的用户付费价值可能扩展到50:50。", "type": "forecast", "timestamp": "00:19:42", "is_estimated": True, "context": "Explaining why Xpeng reframes as physical AI.", "source_quality": "guest_estimate"},
        ],
        "contradictions": [
            {"statement_a": "旧路线更稳定, 下限较好。", "timestamp_a": "00:15:04", "statement_b": "新路线上限更高但下限很惨烈。", "timestamp_b": "00:15:04", "resolution_note": "这是明确的技术取舍: 先打开上限, 再收敛下限。", "type": "qualification"}
        ],
        "predictions": [
            {"prediction": "十年内车或机器人的软件综合能力价值可能达到约50%。", "time_horizon": "未来十年", "confidence": "medium", "conditions": "physical AI能提升上限并守住下限。", "timestamp": "00:19:42"}
        ],
    },
    "seg_03": {
        "topics": [
            {"name": "2025年关键赌注", "description": "从捷径转向大道, 停掉旧体系并重构自动驾驶中心。", "importance": "core", "source_timestamps": ["00:22:36", "00:23:52"], "keywords": ["赌注", "组织架构", "大道"]},
            {"name": "组织变革节奏", "description": "物理AI变革涉及组织、流程和方向, 不能小刀慢砍。", "importance": "core", "source_timestamps": ["00:34:44", "00:35:20"], "keywords": ["组织", "流程", "方向"]},
            {"name": "AI四方向", "description": "数字AI、物理AI、人体AI、企业AI构成当前探索框架。", "importance": "major", "source_timestamps": ["00:36:13"], "keywords": ["数字AI", "人体AI", "企业AI"]},
        ],
        "insights": [
            {"claim": "找到适合自己的道路比学习标杆公司更重要, 因为物理AI无法复制数字AI路径。", "explanation": "何小鹏明确反对学A公司、学B公司, 强调每家公司过去的道路不可复制, 物理世界还包含工程、产品、商品、法规和人。", "type": "反直觉洞察", "source_timestamp": "00:28:05", "confidence": "high", "related_insights": []},
            {"claim": "大组织的AI变革不是工具升级, 而是方法论、流程和组织的根部重构。", "explanation": "他认为内部改动直到根上, 外界看到的业务层只是表面。组织变革以年计, 中型全球组织3年变完已很快。", "type": "因果论断", "source_timestamp": "00:35:20", "confidence": "high", "related_insights": []},
            {"claim": "CEO的焦虑来自底层公理被重构, 不是来自看到更多问题。", "explanation": "在技术剧烈变革期, 旧的价值观、世界观和管理公理都可能失效, 关键是构建既有上限又能堵住下限的体系。", "type": "心智模型", "source_timestamp": "00:38:17", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("这条路是一条捷径，但是不是一条大道，是一条小路。", "00:22:36", "Explaining why Xpeng abandoned the old autonomy path.", ["strategy", "autonomy"]),
            quote("绝不服输，第二个就是愿赌服输。", "00:26:51", "Naming the two mental lines after Xpeng's 2022 challenges.", ["mindset", "bet"]),
            quote("今天中国说学A公司，学B公司，我觉得都是错误的。", "00:28:05", "Rejecting copycat strategy.", ["strategy", "organization"]),
            quote("切忌不要小刀砍大树，慢慢砍，想清楚了砍掉它。", "00:34:44", "Explaining organizational action under uncertainty.", ["organization", "decision"]),
            quote("物理AI它比数字AI可能难100倍。", "00:36:13", "Comparing physical AI with digital AI.", ["physical AI", "difficulty"]),
        ],
        "data_points": [
            {"value": "2025年三季度末小鹏重改自动驾驶中心核心组织架构。", "type": "event", "timestamp": "00:23:52", "is_estimated": False, "context": "Describing the implementation of the strategic bet.", "source_quality": "firsthand"},
            {"value": "何小鹏估计物理AI比数字AI可能难100倍。", "type": "benchmark", "timestamp": "00:36:13", "is_estimated": True, "context": "AI direction taxonomy.", "source_quality": "guest_estimate"},
            {"value": "全球化中型组织3年完成组织变化已是极快速度, 5到10年也算快。", "type": "benchmark", "timestamp": "00:37:49", "is_estimated": True, "context": "Discussing long-term transformation period.", "source_quality": "guest_estimate"},
        ],
        "contradictions": [
            {"statement_a": "内部很多人反对或不确认新路线。", "timestamp_a": "00:33:38", "statement_b": "他要求想清楚后从组织到流程到方向全部改。", "timestamp_b": "00:34:44", "resolution_note": "何小鹏承认不确定, 但把创业定义为在不确定下下注。", "type": "tension"}
        ],
        "predictions": [
            {"prediction": "2027到2028年开始, 物理AI会出现类似ChatGPT带给数字AI的显著效果。", "time_horizon": "2027-2028", "confidence": "medium", "conditions": "物理AI落地到具体岗位。", "timestamp": "00:36:13"},
            {"prediction": "企业AI对小中大型公司都是机会, 但企业级耦合比部门或中心级耦合更难。", "time_horizon": "长期", "confidence": "medium", "conditions": "组织能完成AI耦合。", "timestamp": "00:37:16"},
        ],
    },
    "seg_04": {
        "topics": [
            {"name": "机器人三阶段", "description": "2018-2020独立团队, 2020-2023多方案集成, 2023后转向大脑驱动双足。", "importance": "core", "source_timestamps": ["00:40:46", "00:41:37"], "keywords": ["机器人", "双足", "大脑"]},
            {"name": "团队重构", "description": "300人团队只留不到60人, 用跨AI、汽车、工程、机器人的新团队重构。", "importance": "core", "source_timestamps": ["00:43:54", "00:44:24"], "keywords": ["团队", "LC", "重构"]},
            {"name": "人才潜力", "description": "用超级聪明的人做超级困难的事情, 支持长期探索。", "importance": "major", "source_timestamps": ["00:46:17", "00:47:07"], "keywords": ["人才密度", "博士", "长期探索"]},
        ],
        "insights": [
            {"claim": "机器人路线的关键转折是从不相信大脑, 变成相信大脑驱动机型的全新设计。", "explanation": "旧集成路线取得过成败经验, 但2023年后小鹏认为缺少大脑就不可能成功, 从四足转入双足。", "type": "因果论断", "source_timestamp": "00:41:37", "confidence": "high", "related_insights": []},
            {"claim": "机器人不是技术演示, 它必须穿过技术、产品、商品和规模化四道门。", "explanation": "何小鹏把汽车经验迁移到机器人, 强调技术好不等于产品好, 产品好不等于商品好, 商品好不等于可规模化。", "type": "分析框架", "source_timestamp": "00:41:37", "confidence": "high", "related_insights": []},
            {"claim": "极难问题早期需要人才潜力, 而不是流程化地锻造普通能力。", "explanation": "他强调招募高潜力人才并支持长期探索, 认为方向、流程和工具在某些阶段不如人本身的潜力重要。", "type": "心智模型", "source_timestamp": "00:47:07", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("技术好不代表产品好，产品的好不代表商品好，商品好不代表你可以scare。", "00:41:37", "Explaining why robot commercialization is not a pure technical problem.", ["product", "commercialization"]),
            quote("明年2027年很有可能是机器人在高等级机器人上面进入到商业量产的第一个元年。", "00:42:35", "Forecasting high-grade robot mass production.", ["robotics", "prediction"]),
            quote("要用超级聪明的人去做超级困难的事情。", "00:47:07", "Explaining talent philosophy.", ["talent", "organization"]),
        ],
        "data_points": [
            {"value": "2018-2020、2020-2023、2023年后三个阶段构成小鹏机器人路线。", "type": "date", "timestamp": "00:40:46", "is_estimated": False, "context": "Robot history.", "source_quality": "firsthand"},
            {"value": "原300人机器人团队只留不到60人。", "type": "statistic", "timestamp": "00:43:54", "is_estimated": True, "context": "Robot team reset.", "source_quality": "firsthand"},
            {"value": "一个部门招了接近80个类似清华博士的毕业生。", "type": "statistic", "timestamp": "00:46:17", "is_estimated": True, "context": "Talent investment.", "source_quality": "firsthand"},
        ],
        "contradictions": [
            {"statement_a": "用熟悉机器人团队未必能做出新一代机器人。", "timestamp_a": "00:43:40", "statement_b": "新团队也不能什么都不懂, 需要AI、汽车、工程、机器人交叉。", "timestamp_b": "00:44:24", "resolution_note": "不是反专家, 而是反单一专家结构。", "type": "qualification"}
        ],
        "predictions": [
            {"prediction": "2027年可能成为高等级机器人商业量产元年。", "time_horizon": "2027年", "confidence": "medium", "conditions": "高等级机器人产品进入商业量产。", "timestamp": "00:42:35"},
            {"prediction": "机器人的价值会从情绪价值走向物理价值加情绪价值的组合。", "time_horizon": "2027年起", "confidence": "medium", "conditions": "机器人能够真正帮人干活。", "timestamp": "00:43:25"},
        ],
    },
    "seg_05": {
        "topics": [
            {"name": "造人而不是造机器人", "description": "通用人形路线被定义为社会参与和情绪连接问题, 不是单一商业产品。", "importance": "core", "source_timestamps": ["00:47:34"], "keywords": ["通用人形", "造人", "情绪价值"]},
            {"name": "进入家庭的物理约束", "description": "尺寸、热、安全、恐怖谷、法律和老人小孩场景决定机器人形态。", "importance": "core", "source_timestamps": ["00:49:45", "00:53:06"], "keywords": ["家庭", "安全", "恐怖谷"]},
            {"name": "舆论变成数据", "description": "发布争议暴露真实需求, 尤其家庭干活和养老依赖。", "importance": "major", "source_timestamps": ["00:53:49", "00:55:51"], "keywords": ["舆论", "data", "养老"]},
        ],
        "insights": [
            {"claim": "通用人形机器人路线的核心不是像人, 而是能够进入人的生活半径。", "explanation": "何小鹏用机器狗、双足机器人、老人小孩安全感解释形态选择: 能进入家庭和社会才有基础岗位价值。", "type": "分析框架", "source_timestamp": "00:49:45", "confidence": "high", "related_insights": []},
            {"claim": "大众质疑本身是产品信号, 因为它暴露了用户对家庭劳动和养老陪伴的真实期待。", "explanation": "爆炸性讨论让小鹏看到年轻人希望机器人进家庭干活, 中年以上人群思考未来养老依赖。", "type": "反直觉洞察", "source_timestamp": "00:55:51", "confidence": "high", "related_insights": []},
            {"claim": "机器人难在必须同时解决物理能力、情绪距离和社会规则。", "explanation": "能走、能动只是开始, 还要让人愿意靠近, 让法律、家庭和商业环境接受。", "type": "因果论断", "source_timestamp": "00:51:08", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("他一直跟我说他想是造人而不是造机器人。", "00:47:34", "Explaining the humanoid ambition.", ["humanoid", "vision"]),
            quote("老人很有可能把继承人作为他唯一的依赖。", "00:48:18", "Discussing aging and robot dependence.", ["aging", "robotics"]),
            quote("一只机器狗它百分之百会让你们两个都觉得受伤。", "00:50:27", "Explaining why home-entry robots cannot be designed like pets.", ["home", "safety"]),
            quote("当24个小时之后，可能这个子弹已经不知道飞到哪去了。", "00:53:49", "Explaining why the team responded quickly to public doubts.", ["public opinion", "communication"]),
            quote("机器人创业，我甚至认为远超汽车的创业的难度。", "00:57:10", "Comparing robot startups to car startups.", ["startup", "robotics"]),
        ],
        "data_points": [
            {"value": "小鹏当前一代机器人身高约1米69到1米70。", "type": "statistic", "timestamp": "00:52:58", "is_estimated": True, "context": "Explaining a socially acceptable middle-state humanoid.", "source_quality": "firsthand"},
            {"value": "何小鹏估计机器人创业难度约为汽车创业的20到100倍。", "type": "benchmark", "timestamp": "00:57:10", "is_estimated": True, "context": "Assessing robot startup difficulty.", "source_quality": "guest_estimate"},
            {"value": "发布争议后, 很多年轻人希望机器人进入家庭帮忙干活。", "type": "event", "timestamp": "00:55:51", "is_estimated": False, "context": "Reading social media reaction.", "source_quality": "firsthand"},
        ],
        "contradictions": [
            {"statement_a": "小鹏选择了最像人的人形机器人。", "timestamp_a": "00:58:38", "statement_b": "机器人又不能有自己的脸, 必须和人有差距。", "timestamp_b": "00:53:06", "resolution_note": "目标是生活半径内的可接受人形, 不是完全仿真人。", "type": "tension"}
        ],
        "predictions": [
            {"prediction": "三四年后, 等很多机器人公司踩坑后, 外界会看到小鹏路线差异。", "time_horizon": "3-4年", "confidence": "medium", "conditions": "行业经历真实落地问题。", "timestamp": "00:56:36"},
            {"prediction": "30年后机器人竞争会进入新的状态。", "time_horizon": "30年", "confidence": "tentative", "conditions": "机器人产业进入规模竞争。", "timestamp": "00:56:36"},
        ],
    },
    "seg_06": {
        "topics": [
            {"name": "机器人市场结构", "description": "机器人细分远多于汽车, 通用人形死亡率极高但差异化机器人有多种解法。", "importance": "core", "source_timestamps": ["00:58:10", "00:58:38"], "keywords": ["细分", "通用人形", "差异化"]},
            {"name": "运动控制被低估", "description": "机器人运动控制还没有T型车, 需要全姿态全AI协同。", "importance": "core", "source_timestamps": ["01:00:07", "01:02:08"], "keywords": ["运动控制", "全姿态", "MPC"]},
            {"name": "小鹏三条曲线", "description": "汽车成为智能体, 机器人/集成成为智能体, 以及全球化。", "importance": "major", "source_timestamps": ["01:04:12", "01:04:39"], "keywords": ["三条曲线", "智能体", "全球化"]},
        ],
        "insights": [
            {"claim": "通用人形机器人最大的对手不是同行, 而是自己的组织、模型、产品和工程能力。", "explanation": "何小鹏认为行业仍早, 没有清晰对手, 核心是把底层组织、英法、体系能力和工程能力做强。", "type": "心智模型", "source_timestamp": "00:59:38", "confidence": "high", "related_insights": []},
            {"claim": "机器人运动控制不只是走路或打架, 而是身体、表情、手眼脚和情绪的全协同。", "explanation": "他认为多数公司低估运动控制, 机器人还处于早期汽车时代, 需要像人一样由AI控制复杂本能。", "type": "分析框架", "source_timestamp": "01:02:08", "confidence": "high", "related_insights": []},
            {"claim": "机器人一旦在某个点形成产品突破, 规模化速度可能远超汽车。", "explanation": "汽车受道路、法规、量产和需求波动制约, 机器人如果解决单点刚需可能出现更快扩散。", "type": "因果论断", "source_timestamp": "01:04:39", "confidence": "medium", "related_insights": []},
        ],
        "golden_quotes": [
            quote("如果走通用人形继承，99.99会死掉。", "00:58:38", "Assessing humanoid robot startup survival.", ["humanoid", "startup"]),
            quote("通用人形机器人现在没有对手，全都是自己。", "00:59:38", "Defining the competitive landscape.", ["competition", "capability"]),
            quote("T型车在机器里面肯定还没有。", "01:02:08", "Placing current robots in historical analogy.", ["motion control", "history"]),
            quote("小鹏新的十年有三条曲线。第一条曲线是汽车，把汽车干到完全的智能体，我觉得第二个是集成，集成本身就是智能体。", "01:04:12", "Defining Xpeng's next decade.", ["strategy", "curves"]),
            quote("一旦机器人有能力规模化，它的规模化的速度会远超过汽车。", "01:04:39", "Comparing robot scale speed with cars.", ["scale", "robotics"]),
        ],
        "data_points": [
            {"value": "何小鹏认为机器人公司数量可能比当年汽车公司double, 基金公司据说已有两百多家。", "type": "statistic", "timestamp": "00:57:53", "is_estimated": True, "context": "Comparing robot startup wave with car startup wave.", "source_quality": "guest_estimate"},
            {"value": "小鹏机器人硬件约80%自研或深度参与。", "type": "statistic", "timestamp": "01:05:52", "is_estimated": True, "context": "Explaining quality and scale control.", "source_quality": "firsthand"},
            {"value": "机器人商业化难点包括硬件可靠稳定、多大模型拟合和商业证明。", "type": "other", "timestamp": "01:06:25", "is_estimated": False, "context": "Discussing near-term mass production challenges.", "source_quality": "firsthand"},
        ],
        "contradictions": [
            {"statement_a": "通用人形路线99.99会死掉。", "timestamp_a": "00:58:38", "statement_b": "机器人整体胜率比乘用车高。", "timestamp_b": "00:58:38", "resolution_note": "通用人形极难, 但差异化机器人解法很多。", "type": "qualification"}
        ],
        "predictions": [
            {"prediction": "机器人一旦具备规模化能力, 扩张速度会远超汽车。", "time_horizon": "长期", "confidence": "medium", "conditions": "某个点形成真实刚需和软件能力。", "timestamp": "01:04:39"},
            {"prediction": "第一款商业量产机器人还未达到iPhone 1级别, 市场仍在等待标志性产品。", "time_horizon": "近期", "confidence": "medium", "conditions": "商业量产产品出现。", "timestamp": "01:06:55"},
            {"prediction": "小鹏在通用人形路线上的胜率约两成, 且他认为这已是中国企业里很高。", "time_horizon": "长期战役", "confidence": "medium", "conditions": "以足够大的目标口径计算。", "timestamp": "01:07:35"},
        ],
    },
    "seg_07": {
        "topics": [
            {"name": "G系列高端SUV", "description": "小鹏用高端全尺寸6座SUV重新进入高端市场。", "importance": "core", "source_timestamps": ["01:08:38"], "keywords": ["SUV", "高端", "G系列"]},
            {"name": "跨域融合", "description": "飞行汽车、机器人、线控底盘、VIA和家庭空间能力进入同一车型。", "importance": "core", "source_timestamps": ["01:09:04", "01:10:32"], "keywords": ["飞行汽车", "线控底盘", "机器人"]},
            {"name": "全维度竞争", "description": "高端车不能靠少数亮点, 最差点也要达到80分, 多数点要90/95分。", "importance": "major", "source_timestamps": ["01:11:36"], "keywords": ["全维度", "下限", "差异化"]},
        ],
        "insights": [
            {"claim": "G系列不是单点产品, 而是小鹏把汽车、飞行汽车和机器人能力打通的试验场。", "explanation": "何小鹏强调冗余安全、线控底盘、VIA自动驾驶和机器人任务理解都进入了新车能力组合。", "type": "分析框架", "source_timestamp": "01:09:04", "confidence": "high", "related_insights": []},
            {"claim": "高端汽车竞争的关键是最低点不能差, 而不是某个点特别强。", "explanation": "他延续长板、短板、宽板框架, 认为全尺寸SUV要在外观、内饰、细节、配置、空间、智能等维度同时达标。", "type": "心智模型", "source_timestamp": "01:11:36", "confidence": "high", "related_insights": []},
            {"claim": "小鹏从2022年底到2026年的质变来自组织、产品规划、客户认知和商业逻辑的整体复盘。", "explanation": "他把当前自信归因于三年半积累, 而不是某一代车型或单一技术进步。", "type": "因果论断", "source_timestamp": "01:14:36", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("它就像飞机一样，它允许你有冗余。", "01:09:04", "Explaining flight-car redundancy applied to the SUV.", ["car", "redundancy"]),
            quote("它是把小鹏的自己的很多能力，分析的很多能力，基层的能力，这样是做了一个非常有趣的融合。", "01:10:32", "Describing cross-domain capability fusion.", ["fusion", "product"]),
            quote("你可能你最差的点是80分，然后还有更多的90分跟95，你才有可能在这个战争中间胜出。", "01:11:36", "Explaining high-end product competition.", ["product", "competition"]),
            quote("集汽车是一个非常复杂的技术的人性的经营的大集成体系。", "01:14:56", "Summarizing why car-making is complex.", ["car", "integration"]),
        ],
        "data_points": [
            {"value": "新车型为全尺寸6座旗舰SUV。", "type": "entity", "timestamp": "01:08:38", "is_estimated": False, "context": "Introducing the G-series product.", "source_quality": "firsthand"},
            {"value": "车型设计包含八个安全冗余。", "type": "statistic", "timestamp": "01:09:04", "is_estimated": False, "context": "Flight-car redundancy applied to car design.", "source_quality": "firsthand"},
            {"value": "线控底盘与EEA、VIA联动可提升安全下限、缩短时延、提高控制灵敏度。", "type": "benchmark", "timestamp": "01:09:46", "is_estimated": True, "context": "Chassis and autonomy integration.", "source_quality": "firsthand"},
            {"value": "5月21日将正式发布并给出更清晰配置。", "type": "date", "timestamp": "01:12:04", "is_estimated": False, "context": "Product launch timing mentioned in transcript.", "source_quality": "firsthand"},
        ],
        "contradictions": [
            {"statement_a": "他说做大车面临同质化血海。", "timestamp_a": "01:11:05", "statement_b": "小鹏仍选择做全尺寸高端SUV。", "timestamp_b": "01:08:38", "resolution_note": "差异化来自跨域能力和全维度下限, 而不是简单拼配置。", "type": "tension"}
        ],
        "predictions": [
            {"prediction": "大九系竞争中魏小理会给出各自不同的看法和认知。", "time_horizon": "2026年车展周期", "confidence": "medium", "conditions": "新车型集中发布。", "timestamp": "01:14:08"}
        ],
    },
    "seg_08": {
        "topics": [
            {"name": "CEO时间与成功定义", "description": "何小鹏把最多时间放在战略和规划, 成功不等同于规模或利润。", "importance": "core", "source_timestamps": ["01:16:42"], "keywords": ["战略", "规划", "成功"]},
            {"name": "L4与汽车价值", "description": "L4预计18到24个月可能实现, 但单一能力不是企业长期价值。", "importance": "core", "source_timestamps": ["01:18:31", "01:19:26"], "keywords": ["L4", "VA", "销量"]},
            {"name": "自研、合作与行业集中", "description": "复杂系统中战略能力要自研, 战术能力可合作; 中国规模车企会越来越集中。", "importance": "core", "source_timestamps": ["01:19:52", "01:23:24"], "keywords": ["地平线", "自研", "集中"]},
            {"name": "实践学习与后悔", "description": "知识来自实践和高速循环, AI体系应尽量减少人的循环消耗。", "importance": "major", "source_timestamps": ["01:24:52", "01:25:46"], "keywords": ["实践", "PDCA", "后悔"]},
        ],
        "insights": [
            {"claim": "企业成功不是单一能力胜出, 而是技术、组织、市场、商业规划的组合能力胜出。", "explanation": "何小鹏多次强调汽车和企业最后的成功不来自AI、硬件或销售的单点能力, 而是跨域融合和综合规划。", "type": "分析框架", "source_timestamp": "01:16:42", "confidence": "high", "related_insights": []},
            {"claim": "第三方方案是否成功取决于行业终局是分散还是集中。", "explanation": "如果车企数量多, 第三方道路更广; 如果越来越集中, 第三方道路会更痛苦。", "type": "因果论断", "source_timestamp": "01:19:52", "confidence": "high", "related_insights": []},
            {"claim": "AI体系中的循环应尽量自动化, 传统PDCA的人为检查环节会成为消耗。", "explanation": "他把知识吸收和组织学习放到实践循环中, 认为AI体系要依靠全自动循环而不是传统人工闭环。", "type": "反直觉洞察", "source_timestamp": "01:24:52", "confidence": "high", "related_insights": []},
        ],
        "golden_quotes": [
            quote("汽车做好一件事情不代表能做好，这是一个很痛苦的问题。", "01:17:37", "Explaining why car companies cannot rely on one strength.", ["car", "systems"]),
            quote("我大概率认为18到24个月。", "01:18:31", "Answering when L4 may be realized.", ["L4", "prediction"]),
            quote("汽车和企业的最后的成功，不是仅来自于AI里面的一个能力，或者硬件里面的一个能力，或者在销售里面的一个能力。", "01:19:26", "Explaining compound success.", ["strategy", "systems"]),
            quote("我一直说30年中国可能就五家有规模的汽车企业。", "01:23:24", "Forecasting industry concentration.", ["cars", "prediction"]),
            quote("在AI体系里面要靠全自动的循环，PDC的C都不能做了。", "01:24:52", "Explaining learning in AI systems.", ["PDCA", "automation"]),
        ],
        "data_points": [
            {"value": "何小鹏认为L4对小鹏可能在18到24个月内实现。", "type": "forecast", "timestamp": "01:18:31", "is_estimated": True, "context": "Asked when L4 will be realized.", "source_quality": "guest_estimate"},
            {"value": "2026年4月中国汽车销量同环比下跌约20%, 小鹏约增长50%到70%。", "type": "statistic", "timestamp": "01:18:42", "is_estimated": True, "context": "Discussing second-generation VA impact.", "source_quality": "guest_estimate"},
            {"value": "何小鹏预计30年后中国可能只有5家有规模汽车企业。", "type": "forecast", "timestamp": "01:23:24", "is_estimated": True, "context": "Industry concentration forecast.", "source_quality": "guest_estimate"},
            {"value": "他认为汽车领域未来仍可能每年投入1000亿研发费用做持续创新。", "type": "forecast", "timestamp": "01:20:34", "is_estimated": True, "context": "Explaining why cars are far from smartphone-like maturity.", "source_quality": "guest_estimate"},
        ],
        "contradictions": [
            {"statement_a": "L4会带来销量提升。", "timestamp_a": "01:18:42", "statement_b": "销量提升不代表长期价值。", "timestamp_b": "01:18:42", "resolution_note": "短期商业指标和长期企业价值不是同一件事。", "type": "qualification"}
        ],
        "predictions": [
            {"prediction": "小鹏可能在18到24个月内实现L4。", "time_horizon": "18-24个月", "confidence": "medium", "conditions": "仅或许针对小鹏。", "timestamp": "01:18:31"},
            {"prediction": "汽车企业会越来越集中, 30年后中国可能只有五家有规模车企。", "time_horizon": "30年", "confidence": "medium", "conditions": "规模竞争强度继续上升。", "timestamp": "01:23:24"},
            {"prediction": "机器人同质内卷可能低于汽车, 因为软件价值大且缺少可替代软件能力的开源方案。", "time_horizon": "长期", "confidence": "medium", "conditions": "机器人软件价值持续成为核心。", "timestamp": "01:23:57"},
        ],
    },
}


themes = [
    {
        "id": "theme_1",
        "name": "数字AI不是物理AI答案",
        "description": "数字AI处理语言和信息, 物理AI处理真实世界里的数据、约束、法规和人机关系。",
        "appears_in_segments": ["seg_01", "seg_02", "seg_03"],
        "significance": "这是全场最重要的边界划分, 决定为什么小鹏不能只把AI工具叠加到旧流程上。",
    },
    {
        "id": "theme_2",
        "name": "上限、下限与广度",
        "description": "物理AI产品必须同时打开上限、守住下限、覆盖足够广度, 长板思维不够。",
        "appears_in_segments": ["seg_02", "seg_03", "seg_07", "seg_08"],
        "significance": "解释小鹏为何愿意承受新路线的低下限, 也解释汽车与机器人的产品难度。",
    },
    {
        "id": "theme_3",
        "name": "组织重构比工具应用关键",
        "description": "AI变革的核心不是用工具提效, 而是重构组织、流程、方法论和决策节奏。",
        "appears_in_segments": ["seg_02", "seg_03", "seg_04", "seg_08"],
        "significance": "它把访谈从技术讨论拉回到CEO职责: 在不确定下改组织和下注。",
    },
    {
        "id": "theme_4",
        "name": "机器人是社会入口",
        "description": "人形机器人不是单一硬件, 而是物理价值、情绪价值、家庭场景和社会规则的组合。",
        "appears_in_segments": ["seg_04", "seg_05", "seg_06"],
        "significance": "解释小鹏为什么选择最难的人形路线, 以及为什么单纯demo远远不够。",
    },
    {
        "id": "theme_5",
        "name": "超级难题需要超级人才",
        "description": "物理AI早期不是流程取胜, 而是高潜力人才、跨域团队和长期探索取胜。",
        "appears_in_segments": ["seg_04", "seg_05", "seg_06"],
        "significance": "支撑小鹏从300人团队到不到60人的重构, 也解释其招募和投入逻辑。",
    },
    {
        "id": "theme_6",
        "name": "复合系统靠跨域融合",
        "description": "汽车和机器人都是复合系统, 竞争来自硬件、软件、制造、设计、服务和运营的融合。",
        "appears_in_segments": ["seg_06", "seg_07", "seg_08"],
        "significance": "连接机器人和G系列SUV, 说明小鹏把飞行汽车、机器人、底盘和自动驾驶能力放进同一个体系。",
    },
    {
        "id": "theme_7",
        "name": "愿赌服输的战略观",
        "description": "何小鹏的决策观是在巨大不确定下尽早下注, 承认错误但不沉溺后悔。",
        "appears_in_segments": ["seg_03", "seg_06", "seg_08"],
        "significance": "这是人物画像的核心: 不是无畏, 而是在焦虑中构建新公理并行动。",
    },
]


def build_knowledge():
    knowledge_segments = []
    for seg in segments:
        ext = extractions[seg["id"]]
        knowledge_segments.append(
            {
                "id": seg["id"],
                "title": seg["title"],
                "time_range": seg["time_range"],
                "summary": seg["summary"],
                "key_topics": seg["key_topics"],
                "topics": ext["topics"],
                "insights": ext["insights"],
                "golden_quotes": ext["golden_quotes"],
                "data_points": ext["data_points"],
                "contradictions": ext["contradictions"],
                "predictions": ext["predictions"],
            }
        )
    return {
        "metadata": {
            "title": "未尽之约: 何小鹏谈物理AI、小鹏机器人与汽车战略",
            "date": "2026-06-02",
            "guest": {"name": "何小鹏", "affiliation": "小鹏集团创始人兼CEO"},
            "interviewer": {"name": "张小珺"},
            "total_duration_seconds": 5146,
            "duration": {"total_seconds": 5146, "formatted": "1h 25m 46s"},
            "total_turns": 254,
            "language": "zh",
            "source_file": str((OUT.parent.parent / "transcripts" / "hexiaopeng.docx").resolve()),
        },
        "segments": knowledge_segments,
        "cross_cutting_themes": themes,
        "open_questions": [
            "小鹏的新physical AI路线能否在提升上限后按产品要求收敛下限? [00:15:04]",
            "通用人形机器人在家庭场景里最先被用户付费接受的任务是什么? [00:55:51]",
            "第三方智驾方案在车企集中化终局下能否持续扩张? [01:19:52]",
            "L4实现后到底转化为销量、利润、社会价值还是行业冲击? [01:18:42]",
        ],
    }


def all_items(knowledge, key):
    out = []
    for seg in knowledge["segments"]:
        for item in seg.get(key, []):
            x = dict(item)
            x["segment_id"] = seg["id"]
            x["segment_title"] = seg["title"]
            out.append(x)
    return out


def build_visual(knowledge):
    theme_defs = {
        "theme_1": {
            "summary": "物理AI不是把数字AI工具搬进物理世界, 而是重新处理世界的高维数据、约束和行动。",
            "narrative": "这场访谈的底层分界线是数字AI和物理AI。何小鹏认为数字AI处理的是被人类语言高度压缩后的世界, 而物理世界每天呈现的数据量无法被语言完整概括、描述和复制。\n\n因此, 用数字AI公司的工具逻辑、跑分逻辑或token指标来理解汽车和机器人, 会天然低估物理世界的复杂性。physical AI的模型、数据和方法论都不同, 它要直接面向行动、风险、法规和人的生活半径。",
            "insights": [("seg_01", 1, 4), ("seg_02", 1, 5), ("seg_03", 0, 4)],
            "quotes": [("seg_02", 2), ("seg_03", 4)],
        },
        "theme_2": {
            "summary": "数字产品可以靠长板出圈, 物理产品必须同时抬高上限、守住下限并拓宽窄板。",
            "narrative": "何小鹏反复强调, physical AI不是只看一个高分benchmark。自动驾驶、汽车和机器人都需要面对材料、法规、安全、成本、质量、用户心理等短板。\n\n这也是小鹏愿意停掉旧体系的原因: 旧路径下限较稳, 但上限太低。新路线可能早期下限惨烈, 但有机会打开10万分到100万分的上限, 再通过工程收敛下限。",
            "insights": [("seg_02", 0, 5), ("seg_02", 2, 5), ("seg_07", 1, 4), ("seg_08", 0, 4)],
            "quotes": [("seg_02", 1), ("seg_02", 3), ("seg_07", 2)],
        },
        "theme_3": {
            "summary": "真正的AI变革发生在组织根部, 不是工具层。",
            "narrative": "访谈中最强的管理信号是: 小鹏不是在给旧流程加AI, 而是在改流程、组织和方法论。何小鹏把这类变化称为从根上动刀。\n\n这种变革极其缓慢也极其痛苦。技术可能一个月变完, 组织可能需要5到10年。CEO的任务不是消除所有问题, 而是在不完整信息下确定节奏、下注并建立新的判断公理。",
            "insights": [("seg_03", 1, 5), ("seg_03", 2, 5), ("seg_04", 2, 4), ("seg_08", 2, 4)],
            "quotes": [("seg_03", 3), ("seg_03", 4), ("seg_08", 4)],
        },
        "theme_4": {
            "summary": "人形机器人要进入社会, 首先要让人愿意让它靠近。",
            "narrative": "小鹏选择人形机器人不是因为人形最容易, 而是因为它最可能进入人的生活半径。何小鹏把机器人价值从情绪价值扩展到物理价值加情绪价值, 尤其强调养老、家庭和工作空间。\n\n这条路难在它不是纯机械任务。一个机器人要解决尺寸、热、皮肤、恐怖谷、安全感、法律责任和家庭场景。正因如此, 公开争议反而给小鹏提供了用户需求数据。",
            "insights": [("seg_04", 0, 4), ("seg_05", 0, 5), ("seg_05", 1, 4), ("seg_05", 2, 5)],
            "quotes": [("seg_05", 0), ("seg_05", 1), ("seg_05", 2)],
        },
        "theme_5": {
            "summary": "极难问题早期靠高潜力人才和跨域团队, 不是靠稳定流程复制。",
            "narrative": "机器人团队的故事说明, 何小鹏对人才的看法不是简单的专家崇拜。他不想用纯汽车人, 也不想用纯机器人团队, 而是寻找能同时理解AI、汽车、工程和机器人的跨域组合。\n\n这解释了为什么他愿意用昂贵的年轻博士和高潜力团队做长期探索。对于尚未定义清楚的物理AI, 流程能保证下限, 但打开上限往往靠人。",
            "insights": [("seg_04", 1, 5), ("seg_04", 2, 5), ("seg_06", 0, 4)],
            "quotes": [("seg_04", 2), ("seg_06", 1)],
        },
        "theme_6": {
            "summary": "汽车和机器人竞争是跨域融合能力之战。",
            "narrative": "G系列SUV部分看似偏离AI主题, 其实是在展示physical AI公司的产品化逻辑: 飞行汽车冗余、线控底盘、VIA自动驾驶、机器人任务理解和家庭空间都被放进一辆车。\n\n这延续了何小鹏对复合系统的判断: 做好一个能力不等于做成产品。真正的壁垒来自硬件、软件、制造、设计、服务、运营和组织能力的融合。",
            "insights": [("seg_06", 1, 5), ("seg_07", 0, 5), ("seg_07", 2, 4), ("seg_08", 1, 4)],
            "quotes": [("seg_06", 2), ("seg_07", 0), ("seg_08", 2)],
        },
        "theme_7": {
            "summary": "何小鹏的战略观不是不焦虑, 而是在焦虑中愿赌服输。",
            "narrative": "这场访谈里的何小鹏不是乐观主义模板。他承认焦虑、不确定、内部反对和失败可能性, 但更强调想清楚后早点下注。\n\n这种战略观最终落到两个短句: 绝不服输, 愿赌服输。犯错很多, 但不必后悔; 关键是理解为什么现在看错了, 然后继续循环。",
            "insights": [("seg_03", 0, 5), ("seg_03", 2, 4), ("seg_06", 2, 4), ("seg_08", 2, 5)],
            "quotes": [("seg_03", 1), ("seg_03", 2), ("seg_08", 3)],
        },
    }
    color_map = ["#2563eb", "#dc2626", "#7c3aed", "#059669", "#d97706", "#0891b2", "#be123c"]
    visual_themes = []
    for idx, theme in enumerate(themes):
        td = theme_defs[theme["id"]]
        highlighted = []
        for seg_id, insight_idx, importance in td["insights"]:
            seg = next(s for s in knowledge["segments"] if s["id"] == seg_id)
            ins = seg["insights"][insight_idx]
            highlighted.append(
                {
                    "claim": ins["claim"],
                    "explanation": ins["explanation"],
                    "importance": importance,
                    "source_segments": [seg_id],
                    "key_quote": seg["golden_quotes"][0],
                    "related_data_points": [{"label": dp["type"], "value": dp["value"]} for dp in seg.get("data_points", [])[:1]],
                }
            )
        hquotes = []
        for seg_id, qidx in td["quotes"]:
            seg = next(s for s in knowledge["segments"] if s["id"] == seg_id)
            hquotes.append(seg["golden_quotes"][qidx])
        visual_themes.append(
            {
                "id": theme["id"],
                "name": theme["name"],
                "summary": td["summary"],
                "narrative": td["narrative"],
                "importance": idx + 1,
                "color": color_map[idx],
                "highlighted_insights": highlighted,
                "highlighted_quotes": hquotes,
                "related_themes": [t["id"] for t in themes if t["id"] != theme["id"]][:2],
            }
        )

    curated = []
    for vt in visual_themes:
        for q in vt["highlighted_quotes"][:2]:
            item = dict(q)
            item["belongs_to_theme"] = vt["id"]
            curated.append(item)

    map_nodes = []
    for vt in visual_themes:
        args = []
        for ins in vt["highlighted_insights"][:3]:
            q = ins["key_quote"]
            args.append(
                {
                    "claim": ins["claim"][:50],
                    "importance": ins["importance"],
                    "explanation": ins["explanation"],
                    "insight_type": "综合洞察",
                    "evidence": [
                        {"type": "quote", "text": q["text"][:120], "full_text": q["text"], "timestamp": q["timestamp"]},
                    ],
                }
            )
        preds = []
        for sid in [s for s in knowledge["segments"] if s["id"] in sum([t["appears_in_segments"] for t in themes if t["id"] == vt["id"]], [])]:
            if sid.get("predictions"):
                p = sid["predictions"][0]
                preds.append({"text": p["prediction"], "time_horizon": p["time_horizon"], "confidence": p["confidence"]})
        map_nodes.append({"id": vt["id"], "name": vt["name"], "color": vt["color"], "summary": vt["summary"], "arguments": args, "predictions": preds[:2]})

    return {
        "meta": {
            "title": knowledge["metadata"]["title"],
            "date": knowledge["metadata"]["date"],
            "guest": knowledge["metadata"]["guest"],
            "core_thesis": "小鹏的physical AI战略不是给旧流程加AI, 而是用AI重构物理世界产品、组织和商业系统。",
            "core_thesis_elaboration": "何小鹏把数字AI和物理AI区分为两套方法论。数字AI处理语言和信息, 物理AI处理行动、数据、材料、法规、成本和人机关系。小鹏的战略赌注是停掉旧的AI缝合怪路线, 用新的模型、组织和跨域融合去同时打开上限并收敛下限。",
            "key_takeaways": [
                {"claim": "数字AI不能直接迁移为物理AI。", "elaboration": "物理世界的数据量和约束无法用语言完整压缩, 跑分和token指标不足以描述真实价值。"},
                {"claim": "physical AI产品必须同时解决上限、下限和广度。", "elaboration": "汽车和机器人不是只靠一块长板, 还要把窄板做宽、短板做长。"},
                {"claim": "小鹏真正的赌注是组织和方法论重构。", "elaboration": "旧体系不是小改, 而是从自动驾驶中心到流程和方向的根部变化。"},
                {"claim": "机器人是物理价值和情绪价值的社会入口。", "elaboration": "人形路线难, 但它最有机会进入家庭、养老和人的生活半径。"},
                {"claim": "跨域融合是小鹏的核心竞争逻辑。", "elaboration": "飞行汽车、机器人、底盘、自动驾驶和家庭空间被放进同一套产品体系。"},
                {"claim": "战略下注要早, 但要愿赌服输。", "elaboration": "何小鹏承认不确定和焦虑, 但认为犹豫六个月可能更难成功。"},
            ],
            "most_surprising_insight": {
                "claim": "机器人可能比汽车胜率更高, 但通用人形机器人99.99会死掉。",
                "elaboration": "这不是矛盾: 机器人细分赛道远多于汽车, 差异化解法很多; 但最像人的通用人形路线极难, 死亡率极高。",
                "source_quote": {"text": "如果走通用人形继承，99.99会死掉。", "timestamp": "00:58:38"},
            },
            "role_advice": {
                "executive": "重点看组织重构、战略下注和跨域融合主题。",
                "engineer": "重点看上限/下限、运动控制和physical AI方法论。",
                "investor": "重点看机器人市场结构、行业集中和长期胜率判断。",
            },
            "stats": {
                "duration_formatted": "1h 25m 46s",
                "segment_count": len(segments),
                "insight_count": len(all_items(knowledge, "insights")),
                "quote_count": len(all_items(knowledge, "golden_quotes")),
                "prediction_count": len(all_items(knowledge, "predictions")),
                "theme_count": len(themes),
            },
        },
        "themes": visual_themes,
        "segments": [
            {
                "id": seg["id"],
                "title": seg["title"],
                "time_range": seg["time_range"],
                "synthesis_narrative": f"{seg['title']}在访谈中承担的角色是铺开何小鹏的核心判断: {seg['summary']} 它为后续主题提供了时间戳证据和概念边界。",
                "belongs_to_themes": [t["id"] for t in themes if seg["id"] in t["appears_in_segments"]],
                "highlighted_insights": [
                    {
                        "claim": ins["claim"],
                        "explanation": ins["explanation"],
                        "type": ins["type"],
                        "timestamp": ins["source_timestamp"],
                    }
                    for ins in knowledge["segments"][i]["insights"][:2]
                ],
                "highlighted_quotes": knowledge["segments"][i]["golden_quotes"][:2],
            }
            for i, seg in enumerate(segments)
        ],
        "curated_quotes": curated[:20],
        "map_data": {
            "central_thesis": "physical AI要求重构产品、组织与商业系统",
            "theme_nodes": map_nodes,
            "cross_links": [
                {"source": "theme_1.0", "target": "theme_2.0", "relation": "supports"},
                {"source": "theme_2.1", "target": "theme_6.1", "relation": "extends"},
                {"source": "theme_3.0", "target": "theme_7.0", "relation": "supports"},
                {"source": "theme_4.1", "target": "theme_5.0", "relation": "supports"},
                {"source": "theme_6.0", "target": "theme_7.0", "relation": "extends"},
            ],
            "stats": {
                "insight_count": len(all_items(knowledge, "insights")),
                "quote_count": len(all_items(knowledge, "golden_quotes")),
                "data_point_count": len(all_items(knowledge, "data_points")),
                "prediction_count": len(all_items(knowledge, "predictions")),
                "theme_count": len(themes),
                "segment_count": len(segments),
            },
        },
    }


def make_tldr(knowledge):
    return """# 何小鹏 × 未尽之约：速览

*嘉宾：何小鹏，小鹏集团创始人兼CEO｜时长：1小时25分46秒｜日期：2026-06-02*

## 核心观点

1. **小鹏的physical AI不是把数字AI搬进汽车和机器人, 而是换一套底层方法论。** 何小鹏认为数字AI处理语言, 物理AI处理无法被语言完整概括的现实世界数据和行动约束。*[00:17:40]*
2. **旧的自动驾驶路线被他称为“AI缝合怪”, 因为它用软件流程加AI工具, 上限太低。** 小鹏的赌注是用更大的foundation model先打开上限, 再用工程收敛下限。*[00:16:19]*
3. **物理产品的竞争不是长板竞争, 而是长板、窄板、短板一起竞争。** 品质、成本、材质、细节、法规都可能成为短板, 这解释了汽车和机器人为什么难。*[00:19:05]*
4. **小鹏真正动的是组织根部。** 何小鹏说去年三季度末重改自动驾驶中心核心组织架构, 而不是只在业务层用AI提效。*[00:23:52]*
5. **机器人路线的核心是进入人的生活半径。** 人形不是为了炫技, 而是为了把物理价值和情绪价值带进家庭、养老和工作场景。*[00:48:18]*
6. **高端车和机器人都要靠跨域融合。** 飞行汽车冗余、线控底盘、VIA自动驾驶、机器人任务理解被放进同一套产品体系。*[01:09:04]*
7. **何小鹏的战略观是“绝不服输, 愿赌服输”。** 他承认焦虑和不确定, 但认为想清楚后要早下注, 犹豫六个月可能更难成功。*[00:26:51]*

## 最令人意外的洞察

何小鹏同时说了两句看似矛盾的话: 通用人形机器人“99.99会死掉”, 但机器人的胜率又比乘用车高。它们合在一起才是完整判断: 通用人形是最难路线, 但机器人细分远多于汽车, 医疗、货运、货检、家庭、养老都有不同解法。也就是说, 行业空间大, 但小鹏选择的是最难、最需要跨域融合的一条路。*[00:58:38]*

## 值得引用的金句

> "数字AI实际上某种角度是用人类的language，物理AI不是用人类language的。" — *00:17:40*

> "长板跟窄板，窄板要做宽，短板要做长长板要做的更长。" — *00:19:05*

> "绝不服输，第二个就是愿赌服输。" — *00:26:51*

> "切忌不要小刀砍大树，慢慢砍，想清楚了砍掉它。" — *00:34:44*

> "要用超级聪明的人去做超级困难的事情。" — *00:47:07*

## 适合谁读

适合正在思考AI转型、机器人商业化、智能汽车战略、复杂硬件组织变革的创始人、产品负责人、投资人和工程管理者。

## 阅读指南

时间少先读深度报告的“执行摘要”和“跨领域主题”。做技术路线判断读“从AI汽车到物理AI”和“机器人竞争、运动控制与三条曲线”。做组织和战略判断读“下注、组织重构与企业AI”和“战略规划、L4与行业终局”。
"""


DATA_TYPE_CN = {
    "statistic": "统计数据",
    "event": "事件",
    "forecast": "预测",
    "benchmark": "基准判断",
    "date": "时间节点",
}

CONFIDENCE_CN = {
    "high": "高",
    "medium": "中",
    "low": "低",
    "tentative": "暂定",
}

SEGMENT_BACKGROUND_CN = {
    "seg_01": "这一段从AI工具使用、token指标、数据成本和高级角色skill化切入，铺垫何小鹏对“数字AI”和“物理AI”的区分。",
    "seg_02": "这一段解释小鹏为什么把自己重新定义为物理AI公司，以及何小鹏为什么反对软件流程叠加AI工具的旧路线。",
    "seg_03": "这一段围绕2025年的战略下注、组织重构、内部阻力和企业AI展开，重点是AI变革如何真正进入组织根部。",
    "seg_04": "这一段回顾小鹏机器人路线的三次变化、团队重组和人才密度，说明机器人不是演示项目，而是长期系统工程。",
    "seg_05": "这一段讨论人形机器人为什么必须进入人的生活半径，以及家庭、养老、安全感和社会接受度如何影响产品形态。",
    "seg_06": "这一段分析机器人市场结构、运动控制难点、小鹏三条曲线和机器人规模化速度，强调真正的对手首先是自己。",
    "seg_07": "这一段把飞行汽车、机器人、线控底盘和高端SUV联系起来，展示小鹏如何把跨域能力融合进产品。",
    "seg_08": "这一段讨论CEO时间分配、L4时间判断、自研与合作、行业集中和AI系统学习，收束到小鹏未来十年的战略判断。",
}


def cn_data_type(kind):
    return DATA_TYPE_CN.get(kind, kind)


def cn_confidence(confidence):
    return CONFIDENCE_CN.get(confidence, confidence)


def segment_background(seg):
    return SEGMENT_BACKGROUND_CN.get(seg["id"], seg.get("summary", ""))


def make_report(knowledge):
    quote_count = len(all_items(knowledge, "golden_quotes"))
    pred_count = len(all_items(knowledge, "predictions"))
    topic_sections = []
    for seg in knowledge["segments"]:
        qlines = "\n\n".join(
            [f'> **核心引述** *({q["timestamp"]})*:\n> "{q["text"]}"' for q in seg["golden_quotes"][:2]]
        )
        dlines = "\n".join([f'> - **{cn_data_type(dp["type"])}**：{dp["value"]} *({dp["timestamp"]})*' for dp in seg["data_points"][:3]])
        ilines = "\n\n".join([f"**{ins['claim']}** *({ins['source_timestamp']})*\n\n{ins['explanation']}" for ins in seg["insights"]])
        topic_sections.append(
            f"""### {seg['title']} *({seg['time_range']['start']} - {seg['time_range']['end']})*

#### 背景
{segment_background(seg)}

#### 核心论点

{ilines}

{qlines}

> **数据点：**
{dlines}
"""
        )

    theme_sections = []
    for th in themes:
        theme_sections.append(
            f"""### {th['name']}

{th['description']} 这个主题出现在 {', '.join(th['appears_in_segments'])}。它的重要性在于: {th['significance']}

**跨话题例证:**
- 从 **{knowledge['segments'][int(th['appears_in_segments'][0].split('_')[1])-1]['title']}**: {knowledge['segments'][int(th['appears_in_segments'][0].split('_')[1])-1]['insights'][0]['claim']}
- 从 **{knowledge['segments'][int(th['appears_in_segments'][-1].split('_')[1])-1]['title']}**: {knowledge['segments'][int(th['appears_in_segments'][-1].split('_')[1])-1]['insights'][0]['claim']}
"""
        )

    tensions = []
    for idx, c in enumerate(all_items(knowledge, "contradictions"), 1):
        tensions.append(f"| {idx} | {c['statement_a']} / {c['statement_b']} | {c['timestamp_a']} / {c['timestamp_b']} | {c['resolution_note']} |")
    preds = []
    for idx, p in enumerate(all_items(knowledge, "predictions"), 1):
        preds.append(f"| {idx} | {p['prediction']} | {p['time_horizon']} | {cn_confidence(p['confidence'])} | {p['conditions']} *({p['timestamp']})* |")
    quotes = []
    for seg in knowledge["segments"]:
        quotes.append(f"### {seg['title']}")
        for i, q in enumerate(seg["golden_quotes"], 1):
            quotes.append(f'{i}. *({q["timestamp"]})* "{q["text"]}" — 语境：见“{seg["title"]}”相关讨论。')

    return f"""# 何小鹏 × 未尽之约：深度报告

*嘉宾：何小鹏，小鹏集团创始人兼CEO｜主持：张小珺｜时长：1小时25分46秒｜日期：2026-06-02｜来源：hexiaopeng.docx*

---

## 访谈概览

### 嘉宾简介
何小鹏是小鹏集团创始人兼CEO。访谈中, 他从智能电动车、自动驾驶、机器人和企业AI四个角度解释小鹏为什么从“AI汽车企业”转向“物理AI企业”。他的视角同时包含技术路线、组织重构、商业化和长期产业终局。

### 访谈背景
这是一场围绕physical AI、小鹏机器人、汽车产品战略和AI时代CEO判断方式的长访谈。原始Word转写共254个轮次, 时长约1小时25分46秒。

### 关键数据
| 指标 | 数值 |
|--------|-------|
| 覆盖话题数 | {len(segments)} |
| 提取金句数 | {quote_count} |
| 重要预测数 | {pred_count} |
| 对话轮次 | 254 |

---

## 执行摘要

这场访谈的核心论点是: 小鹏的physical AI战略不是把AI工具叠加到旧的汽车和机器人流程上, 而是要重构物理世界产品的模型、数据、组织、工程和商业系统。何小鹏把过去一类自动驾驶路线称为“AI缝合怪”, 因为它仍然用软件方法论和流程做一个更强的软件, 而不是让AI成为物理世界行动体系的底层驱动。*[00:16:19]*

支撑这个判断的三个框架贯穿全场。第一, 数字AI处理被语言压缩后的世界, 物理AI处理无法被语言还原的真实世界。第二, 物理产品不能只看长板, 还要拓宽窄板、补齐短板、守住下限。第三, AI变革不是工具采购, 而是组织和方法论重构: 小鹏在去年三季度末重改自动驾驶中心核心组织架构, 这是从根上动刀。*[00:17:40, 00:19:05, 00:23:52]*

对读者的启发是: 如果你的业务在物理世界、复杂硬件、强监管、强安全或强人机交互中, 不要直接照搬数字AI公司的路线。你需要判断哪些能力是战术合作, 哪些能力是战略自研, 以及组织是否能承受打开上限后收敛下限的长期过程。

---

## 阅读指南

| 读者类型 | 推荐阅读 | 预计时间 |
|---------------|---------------------|----------------|
| 管理者 / 决策者 | 执行摘要、跨领域主题、战略规划、L4与行业终局 | 10 分钟 |
| 实践者 / 工程师 | 从AI汽车到物理AI、机器人竞争、运动控制与三条曲线 | 20 分钟 |
| 投资人 / 分析师 | 机器人三阶段与人才密度、行业终局预测 | 25 分钟 |
| 快速了解者 | 速览摘要、金句全集 | 5 分钟 |

---

## 话题深度分析

{chr(10).join(topic_sections)}

---

## 跨领域主题

{chr(10).join(theme_sections)}

---

## 矛盾与未解问题

| # | 张力 / 问题 | 出现场景 | 处理状态 |
|---|-------------------|---------|-------------------|
{chr(10).join(tensions)}

---

## 预测总结

| # | 预测 | 时间窗口 | 置信度 | 条件 / 限制 |
|---|-----------|--------------|------------|----------------------|
{chr(10).join(preds)}

---

## 金句全集

{chr(10).join(quotes)}
"""


def make_social():
    return """# 何小鹏这场访谈, 真正讲的不是机器人, 是physical AI公司的活法

何小鹏在《未尽之约》里给了一个很清晰的判断: 小鹏不是要把AI工具加到汽车和机器人上, 而是要把组织、产品、模型、数据和商业系统一起重构。

三个最值得记住的判断:

1. 数字AI和物理AI不是一回事。数字AI处理语言, 物理AI处理真实世界的行动、风险、法规、材料、成本和人机关系。何小鹏说: "数字AI实际上某种角度是用人类的language，物理AI不是用人类language的。" *00:17:40*

2. 物理世界不能只靠长板。汽车和机器人要同时看上限、下限、广度, 还要处理无数短板。他那句很狠: "长板跟窄板，窄板要做宽，短板要做长长板要做的更长。" *00:19:05*

3. AI转型最难的不是工具, 是组织。小鹏去年停掉旧自动驾驶体系, 重改自动驾驶中心核心组织架构。何小鹏的表达是: "切忌不要小刀砍大树，慢慢砍，想清楚了砍掉它。" *00:34:44*

最反直觉的是机器人判断。

他说通用人形机器人"99.99会死掉", 但又认为机器人整体胜率比乘用车高。原因是: 通用人形是最难路线, 但机器人细分远多于汽车, 医疗、货运、家庭、养老、工业都有不同解法。

这也解释为什么小鹏要做一条最难的路: 人形机器人不是为了像人, 而是为了进入人的生活半径。老人、小孩、家庭空间、恐怖谷、安全、法律, 这些都不是demo能解决的。

适合读这份报告的人:
AI转型中的CEO, 复杂硬件产品负责人, 机器人投资人, 自动驾驶工程管理者, 以及所有正在思考"AI到底是工具还是底层方法论"的人。

平台版本:

LinkedIn版本: 强调physical AI与组织重构, 适合企业AI和智能硬件从业者。
X/Twitter串文版本: 以"数字AI不是物理AI答案"开头, 拆成7条观点。
微信公众号: 用"何小鹏的physical AI赌注"做标题, 展开机器人、汽车和组织三条线。

#物理AI #机器人 #智能汽车 #小鹏 #自动驾驶 #组织变革 #AI战略
"""


def make_podcast_script():
    return """HOST: 今天我们用十分钟拆解何小鹏在《未尽之约》里的核心判断。

HOST: 这场访谈表面聊小鹏机器人、G系列高端SUV、自动驾驶和AI工具, 但真正的主线只有一条: physical AI不是把数字AI工具搬进物理世界, 而是重构产品、组织和商业系统。

HOST: 第一层, 数字AI和物理AI不是同一种东西。何小鹏说, 数字AI某种角度是用人类language, 物理AI不是用人类language。数字AI处理高度压缩的信息, 物理AI面对的是车、机器人、材料、法规、人机关系和真实世界里无法穷尽的数据。

GUEST: 长板跟窄板，窄板要做宽，短板要做长长板要做的更长。

HOST: 这句话解释了小鹏为什么不满足于旧自动驾驶路线。旧路线用软件流程叠加AI工具, 他称之为AI缝合怪。它可能下限稳定, 但上限不够。新路线上限更高, 但早期下限更惨烈, 所以需要巨大的工程和组织能力去收敛。

HOST: 第二层, 这不是工具升级, 是组织重构。何小鹏说去年三季度末小鹏重改自动驾驶中心核心组织架构。他的组织原则很直接: 想清楚了就不要小刀砍大树, 要从组织、流程到方向一起改。

GUEST: 绝不服输，第二个就是愿赌服输。

HOST: 第三层, 机器人不是单一硬件。何小鹏为什么坚持最像人的通用人形路线? 因为机器人真正要进入人的生活半径。它要面对老人、小孩、家庭空间、恐怖谷、安全、法律和情绪价值。能走路只是开始, 能被人接受才是入口。

HOST: 他同时给出一个很冷静的判断: 通用人形机器人99.99会死掉, 但机器人整体胜率又比乘用车高。原因是机器人细分赛道远多于汽车, 差异化解法很多, 只是小鹏选择了最难的一条。

HOST: 第四层, 汽车依然是physical AI能力的载体。G系列SUV不是单纯做大车, 而是把飞行汽车冗余、线控底盘、VIA自动驾驶、机器人任务理解和家庭空间融合起来。何小鹏的判断是, 复杂系统竞争不是某个点做到100分, 而是最差点也要到80分, 更多点到90分和95分。

HOST: 最后一个问题: 这对其他企业有什么启发? 如果你的业务在物理世界, 不要急着照搬数字AI公司的路径。你要先判断: 哪些能力是战术合作, 哪些能力必须战略自研? 你的组织能不能承受先打开上限、再收敛下限的过程? 你有没有能力让AI从工具变成底层方法论?

HOST: 何小鹏的答案不是简单乐观。他焦虑, 他承认不确定, 但他选择在不确定里下注。因为在他看来, 犹豫六个月, 可能就更难成功。

HOST: 这就是这场访谈最值得带走的一句话: physical AI不是一个功能, 它是一套新组织。

HOST: 本期结束。建议你打开完整报告, 从"数字AI不是物理AI答案"和"组织重构比工具应用关键"两个主题开始读。
"""


def main():
    turns = read_turns()
    write_json(DATA / "segments.json", segments)
    for seg in segments:
        seg_turns = [t for t in turns if seg["turn_indices"][0] <= t["index"] <= seg["turn_indices"][1]]
        write_json(SEGDIR / f"{seg['id']}.json", {**seg, "turns": seg_turns})
        write_json(SEGDIR / f"{seg['id']}_extraction.json", extractions[seg["id"]])
    knowledge = build_knowledge()
    write_json(DATA / "knowledge.json", knowledge)
    visual = build_visual(knowledge)
    write_json(DATA / "visual_content.json", visual)
    (REPORTS / "tldr-hexiaopeng-20260602.md").write_text(make_tldr(knowledge), encoding="utf-8")
    (REPORTS / "report-hexiaopeng-20260602.md").write_text(make_report(knowledge), encoding="utf-8")
    (REPORTS / "social-hexiaopeng-20260602.md").write_text(make_social(), encoding="utf-8")
    (AUDIO / "podcast-script-hexiaopeng-20260602.md").write_text(make_podcast_script(), encoding="utf-8")


if __name__ == "__main__":
    main()
