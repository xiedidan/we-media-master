from typing import TypedDict, Optional


class ArticleTypeConfig(TypedDict):
    name: str
    display_name: str
    description: str
    structure: str
    writing_tips: list[str]
    tone: str
    need_references: bool


ARTICLE_TYPES: dict[str, ArticleTypeConfig] = {
    "essay": {
        "name": "essay",
        "display_name": "感悟类散文",
        "description": "情感表达为主，个人思考为辅的抒情文章",
        "structure": "场景引入+情感铺垫+思考升华",
        "writing_tips": [
            "从具体场景或故事切入",
            "细节描写要生动具体",
            "情感要真实不矫情",
            "结尾要升华到人生或哲理层面",
        ],
        "tone": "感性细腻，真诚自然",
        "need_references": False,
    },
    "tool": {
        "name": "tool",
        "display_name": "工具文/干货",
        "description": "实用性强，步骤清晰的技能分享文章",
        "structure": "痛点引入+方案介绍+步骤说明+效果展示",
        "writing_tips": [
            "开篇要直击痛点",
            "步骤要清晰可操作",
            "每个步骤要有具体说明",
            "最好有效果对比或案例",
        ],
        "tone": "专业清晰，易懂实用",
        "need_references": True,
    },
    "guide": {
        "name": "guide",
        "display_name": "办事攻略",
        "description": "指导性明确，步骤详细的教程类文章",
        "structure": "背景说明+前置条件+步骤流程+常见问题",
        "writing_tips": [
            "说明适用场景和前置条件",
            "步骤要完整无遗漏",
            "标注关键节点和注意事项",
            "收集常见问题并给出解答",
        ],
        "tone": "严谨准确，清晰详细",
        "need_references": False,
    },
    "opinion": {
        "name": "opinion",
        "display_name": "观点输出",
        "description": "立场鲜明，论据充分的观点文章",
        "structure": "背景引入+观点提出+论据支撑+升华总结",
        "writing_tips": [
            "观点要鲜明有新意",
            "论据要有说服力",
            "论证逻辑要严密",
            "结尾要有启发性和延展性",
        ],
        "tone": "理性深刻，有感染力",
        "need_references": True,
    },
    "story": {
        "name": "story",
        "display_name": "故事叙事",
        "description": "以故事形式讲述经历或案例",
        "structure": "背景铺陈+冲突发生+转折解决+启示总结",
        "writing_tips": [
            "情节要一波三折有吸引力",
            "人物要立体有特点",
            "细节描写要有画面感",
            "结尾要点题并升华",
        ],
        "tone": "生动有趣，引人入胜",
        "need_references": False,
    },
    "review": {
        "name": "review",
        "display_name": "测评推荐",
        "description": "对产品或服务进行评测推荐",
        "structure": "需求场景+产品介绍+实测体验+优缺点+推荐建议",
        "writing_tips": [
            "明确目标用户和使用场景",
            "评测要客观全面",
            "优缺点要如实描述",
            "推荐建议要中肯实用",
        ],
        "tone": "客观专业，真实可信",
        "need_references": False,
    },
}


class ArticleTypeRegistry:
    _instance: Optional["ArticleTypeRegistry"] = None

    def __init__(self):
        self.types = ARTICLE_TYPES

    @classmethod
    def get_instance(cls) -> "ArticleTypeRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, type_id: str) -> Optional[ArticleTypeConfig]:
        return self.types.get(type_id)

    def list_types(self) -> list[ArticleTypeConfig]:
        return list(self.types.values())

    def list_type_ids(self) -> list[str]:
        return list(self.types.keys())


def get_article_type(type_id: str) -> Optional[ArticleTypeConfig]:
    registry = ArticleTypeRegistry.get_instance()
    return registry.get(type_id)


def list_all_article_types() -> list[ArticleTypeConfig]:
    registry = ArticleTypeRegistry.get_instance()
    return registry.list_types()


def list_article_type_ids() -> list[str]:
    registry = ArticleTypeRegistry.get_instance()
    return registry.list_type_ids()


if __name__ == "__main__":
    for t in list_all_article_types():
        print(f"{t['display_name']}: {t['description']}")