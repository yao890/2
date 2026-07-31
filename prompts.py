# prompts.py
# 文案生成器 - 提示词模板库（增强版）
# 核心设计：平台规则 + 风格语气 + 内容结构 + 少样本示例 + 负向约束
# 版本：v2.0 增强对话流畅性与内容贴合度

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ============================================================
# 一、风格词汇库（语气词 + 特色表达）
# ============================================================

STYLE_VOCABULARY = {
    # ---------- 专业风格 ----------
    "专业": {
        "keywords": [
            "数据驱动", "底层逻辑", "赋能", "垂直领域",
            "方法论", "闭环", "颗粒度", "复盘",
            "策略", "模型", "洞察", "迭代",
            "ROI", "转化率", "用户画像", "赛道"
        ],
        "sentence_starters": [
            "从数据来看，", "基于底层逻辑分析，", "这套方法论的核心在于",
            "在垂直领域中，", "经过系统复盘，", "策略层面需要关注"
        ],
        "tone": "理性、严谨、有说服力"
    },

    # ---------- 幽默风格 ----------
    "幽默": {
        "keywords": [
            "绝绝子", "YYDS", "破防了", "栓Q",
            "笑不活了", "我真的会谢", "主打一个", "家人们谁懂啊",
            "离谱", "上头", "下头", "社死",
            "显眼包", "i人/e人", "精神状态良好", "芭比Q了"
        ],
        "sentence_starters": [
            "笑死，", "谁懂啊，", "主打一个真实，",
            "家人们，", "真的会谢，", "这波操作，",
            "离谱他妈给离谱开门，"
        ],
        "tone": "轻松、诙谐、有网感"
    },

    # ---------- 亲切风格 ----------
    "亲切": {
        "keywords": [
            "咱们", "放心", "超简单", "慢慢来",
            "一起", "试试看", "真的不难", "手把手",
            "贴心", "悄悄告诉你", "我懂你", "别担心",
            "一步一步", "有手就行", "你值得", "我们"
        ],
        "sentence_starters": [
            "咱们今天聊点实在的，", "你放心，", "超简单的，",
            "来，我们一起", "我懂你的感受，", "别担心，",
            "悄悄告诉你，", "一步一步来，"
        ],
        "tone": "温暖、鼓励、拉近距离"
    }
}


# ============================================================
# 二、平台规则模板（结构 + 约束）
# ============================================================

PLATFORM_RULES = {
    # ---------- 小红书 ----------
    "小红书": {
        "structure": [
            "hook",        # 开篇钩子（1-2句）
            "experience",  # 亲身体验/故事分享
            "tips",        # 干货/建议（分点）
            "feeling",     # 真实感受/情绪表达
            "tags"         # 话题标签
        ],
        "separator": "✨ / 💡 / 📝 / 🌟 / 🏷️",
        "constraints": {
            "min_words": 200,
            "max_words": 300,
            "must_have": ["emoji", "hashtags", "first_person"]
        },
        "template": """
【小红书文案模板】

{emoji_hook} {hook_content}

{emoji_exp} 说真的，{experience_content}

{emoji_tips} {tips_content}

{emoji_feel} {feeling_content}

{emoji_tags} {tags_content}
""",
        "description": "表情符号分隔 + 亲身体验感 + 话题标签 + 200-300字"
    },

    # ---------- 公众号 ----------
    "公众号": {
        "structure": [
            "title",       # 吸睛标题
            "pain_point",  # 痛点引入
            "value",       # 干货分段（2-3段）
            "summary",     # 金句总结
            "call_to_action"  # 引导关注
        ],
        "separator": "## / 📌 / 💎",
        "constraints": {
            "min_words": 800,
            "max_words": 1500,
            "must_have": ["title", "structured_sections", "call_to_action"]
        },
        "template": """
【公众号文案模板】

## 标题：{title_content}

📌 {pain_point_content}

💎 干货一：{value_1}
💎 干货二：{value_2}
💎 干货三：{value_3}

{summary_content}

---
👆 关注我，{call_to_action_content}
""",
        "description": "标题吸睛 + 痛点引入 + 干货分段 + 金句总结 + 引导关注"
    },

    # ---------- 抖音 ----------
    "抖音": {
        "structure": [
            "hook_3s",     # 前3秒钩子
            "content",     # 口语化短句（3-5句）
            "interaction"  # 强烈互动提问
        ],
        "separator": "🔥 / 💬 / 👇",
        "constraints": {
            "min_words": 50,
            "max_words": 120,
            "must_have": ["hook_3s", "interaction_question", "spoken_language"]
        },
        "template": """
【抖音口播文案模板】

🔥 {hook_3s_content}

💬 {content_line_1}
💬 {content_line_2}
💬 {content_line_3}
💬 {content_line_4}

👇 {interaction_content}
""",
        "description": "前3秒钩子 + 口语化短句 + 强烈互动提问（评论区留言）"
    }
}


# ============================================================
# 三、风格示例库（Few-shot Examples）—— 让AI模仿真实语感
# ============================================================

FEW_SHOT_EXAMPLES: Dict[Tuple[str, str], str] = {
    # ---------- 小红书 × 亲切 ----------
    ("小红书", "亲切"): """
✨ 谁懂啊！换季敏感肌终于有救了！

💡 说真的，我以前每到春秋脸就红得像猴屁股，试了十几种面霜都没用。后来听皮肤科朋友说，**精简护肤+修护屏障**才是正解。

📝 超简单，就三步：
1️⃣ 早上清水洗脸，别用洗面奶折腾
2️⃣ 只涂含神经酰胺的修护霜（厚敷！）
3️⃣ 出门硬防晒（帽子口罩比防晒霜温和）

🌟 我坚持了28天，现在皮肤稳得一批，泛红起皮都拜拜啦～

🏷️ #敏感肌护肤 #换季必备 #修护屏障 #精简护肤
""",

    # ---------- 小红书 × 幽默 ----------
    ("小红书", "幽默"): """
✨ 家人们谁懂啊！跟风买的这玩意居然让我原地封神！

💡 说真的，我本来是个厨房杀手，结果这个空气炸锅让我直接变中华小当家！炸鸡翅外酥里嫩，连我老公都问是不是外卖叫的😂

📝 懒人食谱拿走不谢：
1️⃣ 鸡翅划几刀，生抽蚝油腌20分钟
2️⃣ 200度烤15分钟，翻面再5分钟
3️⃣ 撒上辣椒面，香到邻居敲门！

🌟 主打一个零失败，有手就行！

🏷️ #空气炸锅美食 #懒人食谱 #厨房小白 #真香现场
""",

    # ---------- 小红书 × 专业 ----------
    ("小红书", "专业"): """
💡 私域运营的底层逻辑，一篇笔记讲透！

📊 数据驱动告诉你：90%的人做私域，第一步就错了。

📝 核心方法论：
1️⃣ 用户分层：按RFM模型分出高价值用户，优先服务
2️⃣ 内容赋能：在垂直领域，干货打开率是广告的3倍
3️⃣ 闭环迭代：每周复盘转化漏斗，颗粒度细到每句话术

🌟 私域的本质，是把同一批用户的价值做到极致。

🏷️ #私域运营 #用户增长 #数据驱动 #底层逻辑
""",

    # ---------- 公众号 × 专业 ----------
    ("公众号", "专业"): """
## 标题：私域ROI翻倍的底层逻辑，90%的人搞反了方向

📌 很多企业做私域，上来就拉群发优惠券，结果沉默率高达80%。问题出在哪？**把“流量”当成了“留量”**。

💎 干货一：用户分层是前提
数据驱动不是看总量，而是看RFM模型（最近一次消费、频率、金额）。头部20%的用户贡献了60%的GMV，先服务好他们。

💎 干货二：内容赋能代替硬广
在垂直领域，知识干货的打开率是营销内容的3倍。把产品卖点转化为用户痛点解决方案。

💎 干货三：闭环迭代
每周复盘打开率、转化率、裂变率，颗粒度细到每一条话术。

**私域的本质，是把同一批用户的价值做到极致，而不是无限拉新。**

👆 关注我，回复“私域”领取完整SOP表格。
""",

    # ---------- 公众号 × 亲切 ----------
    ("公众号", "亲切"): """
## 标题：新手妈妈别慌！辅食添加真的超简单，手把手教你

📌 你是不是也看着各种辅食表头大？怕宝宝过敏、怕营养不够、怕自己手残……咱们都经历过。

💎 第一步：从单一泥糊开始
放心，第一口就选高铁米粉，冲稀一点，喂一两勺就行。观察3天，没过敏再加新食物。

💎 第二步：慢慢过渡到碎末状
7个月后可以加菜泥、肉泥，咱们一步一步来，不用追求花样，宝宝接受就好。

💎 第三步：培养自主进食
10个月左右给手指食物，蒸软的胡萝卜条、土豆块，让宝宝自己抓，脏点没关系，关键是他超有成就感！

**辅食不是竞赛，每个宝宝都有自己的节奏。你做得已经很棒了～**

👆 关注我，每周更新一篇辅食日记，陪你一起慢慢长大。
""",

    # ---------- 抖音 × 幽默 ----------
    ("抖音", "幽默"): """
🔥 周五下午四点，你的精神状态belike：

💬 身体还在工位，灵魂已经环游世界三圈了
💬 电脑打开八个网页，没一个和工作有关
💬 老板走过来了，假装眉头紧锁盯着Excel
💬 实则心里在默念：倒计时2小时，稳住！

👇 家人们，谁懂啊？你现在是哪种状态？评论区对号入座！
""",

    # ---------- 抖音 × 亲切 ----------
    ("抖音", "亲切"): """
🔥 姐妹们，早上起床脸肿成包子？3分钟急救消肿法来了！

💬 咱们先从耳后淋巴开始，用指腹轻轻打圈按30秒
💬 然后从下巴推至耳根，重复10次，超简单
💬 最后用冷毛巾敷一下眼周，立刻精神了

👇 你学会了吗？明天早上试试看，回来告诉我效果！
""",

    # ---------- 抖音 × 专业 ----------
    ("抖音", "专业"): """
🔥 3个数据驱动的习惯，让你工作效率翻倍！

💬 第一，每天开工先列三件最重要的事，别被琐事带跑
💬 第二，每件事设定截止时间，制造紧迫感
💬 第三，下班前复盘完成度，找到瓶颈环节

👇 你现在的效率瓶颈在哪？评论区告诉我，帮你分析！
"""
}


# ============================================================
# 四、AI味儿禁忌词库（负向约束）
# ============================================================

FORBIDDEN_WORDS = [
    "首先", "其次", "最后", "总之", "综上所述",
    "值得注意的是", "不可否认", "在一定程度上",
    "众所周知", "不言而喻", "毋庸置疑",
    "起着至关重要的作用", "具有深远的意义"
]

FORBIDDEN_PATTERNS = [
    "不仅...而且...", "既...又...", "一方面...另一方面..."
]


# ============================================================
# 五、组合数据结构
# ============================================================

@dataclass
class PromptConfig:
    """提示词配置：平台 + 风格 + 内容主题"""
    platform: str          # 平台名称
    style: str             # 风格名称
    topic: str             # 内容主题
    extra_context: Optional[str] = None  # 额外上下文

    def __post_init__(self):
        self.platform = self.platform.strip()
        self.style = self.style.strip()
        # 自动匹配风格词汇库
        if self.style not in STYLE_VOCABULARY:
            self.style = "亲切"  # 默认回退
        if self.platform not in PLATFORM_RULES:
            self.platform = "小红书"  # 默认回退


# ============================================================
# 六、拼接公式引擎（增强版）
# ============================================================

class PromptComposer:
    """
    组合逻辑：平台规则 + 风格语气 + 内容结构 + 少样本示例 + 负向约束
    拼接公式：platform_rules + style_vocabulary + few_shot_example + forbidden_list + topic_context
    """

    def __init__(self, config: PromptConfig):
        self.config = config
        self.platform_rule = PLATFORM_RULES[config.platform]
        self.style_vocab = STYLE_VOCABULARY[config.style]

    def compose(self) -> str:
        """执行拼接，生成最终提示词（丰富版，带示例和禁词）"""
        parts = []

        # -------- 1. 角色设定 --------
        parts.append("# 角色设定")
        parts.append("你是一位资深文案策划师，擅长高转化、高互动的营销文案。")
        parts.append(f"当前风格是「{self.config.style}」：{self.style_vocab['tone']}")
        parts.append("")

        # -------- 2. 平台规则 --------
        parts.append("# 平台规则")
        parts.append(f"目标平台：{self.config.platform}")
        parts.append(f"特点：{self.platform_rule['description']}")
        parts.append(f"字数限制：{self.platform_rule['constraints']['min_words']}-{self.platform_rule['constraints']['max_words']}字")
        parts.append(f"必须包含：{', '.join(self.platform_rule['constraints']['must_have'])}")
        parts.append("")

        # -------- 3. 内容结构 --------
        parts.append("# 内容结构要求")
        structure_map = {
            "小红书": [
                ("开篇钩子", "用1-2句抓住注意力"),
                ("亲身体验", "分享真实经历，增加可信度"),
                ("干货建议", "分点列出，清晰实用"),
                ("情感表达", "说出真实感受，引发共鸣"),
                ("话题标签", "添加相关热门标签")
            ],
            "公众号": [
                ("吸睛标题", "制造悬念或利益点"),
                ("痛点引入", "戳中用户需求或焦虑"),
                ("干货分段", "分3段输出核心价值"),
                ("金句总结", "一句话升华主题"),
                ("引导关注", "自然植入关注引导")
            ],
            "抖音": [
                ("3秒钩子", "前3句话必须留住用户"),
                ("口语内容", "用4句左右短句讲清核心"),
                ("互动提问", "提出一个让用户想评论的问题")
            ]
        }
        for item in structure_map.get(self.config.platform, []):
            parts.append(f"- {item[0]}：{item[1]}")
        parts.append("")

        # -------- 4. 风格词汇强制植入 --------
        parts.append("# 风格关键词（必须在文案中自然出现至少3个）")
        selected_keywords = self.style_vocab["keywords"][:5]
        parts.append(f"必须融入：{', '.join(selected_keywords)}")
        parts.append(f"推荐句式开头：{', '.join(self.style_vocab['sentence_starters'][:2])}")
        parts.append("")

        # -------- 5. 少样本示例（Few-shot）模仿语感 --------
        parts.append("# ⭐ 风格参考范例（请严格模仿这个语感、断句和情绪节奏）")
        example_key = (self.config.platform, self.config.style)
        if example_key in FEW_SHOT_EXAMPLES:
            parts.append(FEW_SHOT_EXAMPLES[example_key].strip())
        else:
            # 回退：给一个通用示例（小红书×亲切）
            parts.append(FEW_SHOT_EXAMPLES.get(("小红书", "亲切"), "").strip())
        parts.append("")

        # -------- 6. AI味儿禁忌清单（负向约束） --------
        parts.append("# ❌ 绝对禁止的AI书面语（出现即不合格）")
        parts.append(f"禁词：{'、'.join(FORBIDDEN_WORDS[:8])}")
        parts.append(f"禁句式：{'、'.join(FORBIDDEN_PATTERNS)}")
        parts.append("✅ 要求：全部用口语短句，多用语气词（啊、呀、吧、啦、呗），多用省略号或破折号制造停顿感。")
        parts.append("")

        # -------- 7. 创作主题 --------
        parts.append("# 创作主题")
        parts.append(f"主题：{self.config.topic}")
        if self.config.extra_context:
            parts.append(f"补充信息：{self.config.extra_context}")
        parts.append("")

        # -------- 8. 输出模板 --------
        parts.append("# 输出格式（请严格按此模板填充内容）")
        parts.append(self.platform_rule["template"])
        parts.append("")

        # -------- 9. 流畅度额外叮嘱 --------
        parts.append("# 流畅度要求")
        parts.append("- 段落之间用表情符号或短句自然过渡，不要生硬拼接")
        parts.append("- 如果是小红书，体验感要具体到细节（时间、数字、触感）")
        parts.append("- 如果是抖音，每句话不超过15个字，像面对面聊天")
        parts.append("- 如果是公众号，段落之间用过渡句承上启下")

        return "\n".join(parts)

    def compose_short(self) -> str:
        """生成精简版提示词（用于快速测试，也包含示例和禁词）"""
        example_key = (self.config.platform, self.config.style)
        example = FEW_SHOT_EXAMPLES.get(example_key, "")
        # 提取示例的第一行作为语感参考
        sample_line = ""
        if example:
            lines = example.strip().split("\n")
            # 取第一个非空行（通常是表情符号开头）
            for line in lines:
                if line.strip():
                    sample_line = line.strip()
                    break

        return f"""
你是{self.config.style}风格的文案师，为{self.config.platform}平台撰写关于「{self.config.topic}」的文案。

【平台规则】{self.platform_rule['description']}
【风格要求】{self.style_vocab['tone']}，融入关键词：{', '.join(self.style_vocab['keywords'][:4])}
【字数要求】{self.platform_rule['constraints']['min_words']}-{self.platform_rule['constraints']['max_words']}字
【结构要求】{', '.join([s[0] for s in self.platform_rule['structure']])}

【语感模仿】像这样说话：{sample_line[:50] + "..." if len(sample_line)>50 else sample_line}
【禁止使用】{', '.join(FORBIDDEN_WORDS[:5])} 等书面化词语

请直接输出符合平台规范的完整文案，不要解释。
"""


# ============================================================
# 七、工厂函数（便捷调用）
# ============================================================

def create_prompt(
    platform: str,
    style: str,
    topic: str,
    extra_context: Optional[str] = None,
    short_mode: bool = False
) -> str:
    """
    快速生成提示词

    Args:
        platform: 平台名称 (小红书/公众号/抖音)
        style: 风格 (专业/幽默/亲切)
        topic: 主题内容
        extra_context: 额外上下文信息
        short_mode: 是否使用精简模式

    Returns:
        完整的提示词字符串
    """
    config = PromptConfig(platform, style, topic, extra_context)
    composer = PromptComposer(config)
    if short_mode:
        return composer.compose_short()
    return composer.compose()


# ============================================================
# 八、使用示例 & 测试
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("文案生成器提示词模板库 - 测试运行")
    print("=" * 70)

    # ---------- 示例1：小红书 + 亲切风格（完整版） ----------
    print("\n【示例1】小红书 × 亲切 × 护肤 (完整模式)")
    print("-" * 70)
    prompt1 = create_prompt(
        platform="小红书",
        style="亲切",
        topic="换季敏感肌护肤指南",
        extra_context="目标用户是25-35岁敏感肌女性，预算中等"
    )
    print(prompt1[:500] + "...\n（篇幅较长，截取前500字符）")

    # ---------- 示例2：公众号 + 专业风格（精简版） ----------
    print("\n【示例2】公众号 × 专业 × 运营 (精简模式)")
    print("-" * 70)
    prompt2 = create_prompt(
        platform="公众号",
        style="专业",
        topic="私域流量运营的底层逻辑",
        extra_context="面向中小企业主，需要实操性强的内容",
        short_mode=True
    )
    print(prompt2)

    # ---------- 示例3：抖音 + 幽默风格（精简版） ----------
    print("\n【示例3】抖音 × 幽默 × 职场 (精简模式)")
    print("-" * 70)
    prompt3 = create_prompt(
        platform="抖音",
        style="幽默",
        topic="当代打工人周五精神状态",
        short_mode=True
    )
    print(prompt3)

    # ---------- 示例4：批量生成不同组合（精简版） ----------
    print("\n【示例4】批量生成多个组合的提示词")
    print("-" * 70)
    combinations = [
        ("小红书", "专业", "AI工具提效副业"),
        ("小红书", "幽默", "周末宅家神仙吃法"),
        ("公众号", "亲切", "新手妈妈辅食全攻略"),
        ("抖音", "专业", "3个提升专注力的方法"),
    ]

    for platform, style, topic in combinations:
        short = create_prompt(platform, style, topic, short_mode=True)
        print(f"\n--- {platform} × {style} × {topic} ---")
        print(short.strip())
        print("-" * 40)