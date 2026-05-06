from typing import TypedDict, Optional


class PlatformConfig(TypedDict):
    name: str
    display_name: str
    min_length: int
    max_length: int
    style_features: list[str]
    structure_template: str
    tips: list[str]


PLATFORMS: dict[str, PlatformConfig] = {
    "wechat": {
        "name": "wechat",
        "display_name": "微信公众号",
        "min_length": 1500,
        "max_length": 5000,
        "style_features": [
            "观点鲜明",
            "语言简洁",
            "专业但易懂",
            "关注转化",
        ],
        "structure_template": "开头吸引+中间3-5观点+结尾总结行动",
        "tips": [
            "开头用故事或数据切入",
            "中间每个观点要有案例支撑",
            "结尾要有明确的行动号召",
            "避免过于学术化的表达",
        ],
    },
    "zhihu": {
        "name": "zhihu",
        "display_name": "知乎",
        "min_length": 2000,
        "max_length": 8000,
        "style_features": [
            "理性分析",
            "逻辑严密",
            "专业性强",
            "兼顾可读性",
        ],
        "structure_template": "问题定义+原因分析+解决方案+案例支撑",
        "tips": [
            "开篇明确回答核心问题",
            "分析要有数据或案例支撑",
            "提供可操作的解决方案",
            "结尾可以讨论延伸问题",
        ],
    },
    "xiaohongshu": {
        "name": "xiaohongshu",
        "display_name": "小红书",
        "min_length": 300,
        "max_length": 1000,
        "style_features": [
            "轻松活泼",
            "生活化",
            "真实感强",
            "视觉化表达",
        ],
        "structure_template": "痛点引入+解决方案+效果展示",
        "tips": [
            "标题要有吸引力，能引发好奇",
            "内容要真实，有代入感",
            "多用emoji增加视觉感",
            "结尾引导互动评论",
        ],
    },
    "bilibili": {
        "name": "bilibili",
        "display_name": "B站",
        "min_length": 1500,
        "max_length": 4000,
        "style_features": [
            "幽默有梗",
            "专业不失趣味",
            "网感强",
            "弹幕友好",
        ],
        "structure_template": "开场吸引+干货输出+互动引导",
        "tips": [
            "开场要有记忆点",
            "干货要用通俗的方式表达",
            "可以适当玩梗增加亲近感",
            "结尾引导一键三连",
        ],
    },
}


class PlatformRegistry:
    _instance: Optional["PlatformRegistry"] = None

    def __init__(self):
        self.platforms = PLATFORMS

    @classmethod
    def get_instance(cls) -> "PlatformRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, platform_id: str, config: PlatformConfig) -> None:
        self.platforms[platform_id] = config

    def get(self, platform_id: str) -> Optional[PlatformConfig]:
        return self.platforms.get(platform_id)

    def list_platforms(self) -> list[PlatformConfig]:
        return list(self.platforms.values())

    def list_platform_ids(self) -> list[str]:
        return list(self.platforms.keys())


def get_platform(platform_id: str) -> Optional[PlatformConfig]:
    registry = PlatformRegistry.get_instance()
    return registry.get(platform_id)


def list_all_platforms() -> list[PlatformConfig]:
    registry = PlatformRegistry.get_instance()
    return registry.list_platforms()


def list_platform_ids() -> list[str]:
    registry = PlatformRegistry.get_instance()
    return registry.list_platform_ids()


if __name__ == "__main__":
    for p in list_all_platforms():
        print(f"{p['display_name']}: {p['min_length']}-{p['max_length']}字")