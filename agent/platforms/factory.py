from typing import TypedDict, Optional
from agent.platforms.registry import get_platform, list_platform_ids
from agent.platforms.article_types import get_article_type, list_article_type_ids


class AgentConfig(TypedDict):
    platform_id: str
    article_type_id: str
    custom_prompt: Optional[str]


class AgentFactory:
    def __init__(self):
        self.base_system_prompt = self._load_base_prompt()
        self.base_user_template = self._load_user_template()

    def _load_base_prompt(self) -> str:
        try:
            import yaml
            with open("config/prompts.yml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("system_prompt", "")
        except Exception:
            return "你是一位专业的自媒体文章写作大师。"

    def _load_user_template(self) -> str:
        try:
            import yaml
            with open("config/prompts.yml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("user_prompt_template", "")
        except Exception:
            return "请根据以下素材，写一篇关于{topic}的文章。"

    def _load_platform_config(self, platform_id: str, article_type_id: str) -> Optional[dict]:
        import os
        config_path = f"config/platforms/{platform_id}_{article_type_id}.yml"
        if not os.path.exists(config_path):
            return None
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    def create_agent(
        self,
        platform_id: str,
        article_type_id: str,
    ) -> tuple[str, str]:
        platform = get_platform(platform_id)
        article_type = get_article_type(article_type_id)

        if not platform:
            raise ValueError(f"Unknown platform: {platform_id}")
        if not article_type:
            raise ValueError(f" Unknown article type: {article_type_id}")

        custom_config = self._load_platform_config(platform_id, article_type_id)
        if custom_config:
            return custom_config["system_prompt"], custom_config["user_prompt_template"]

        system_prompt = self._build_system_prompt(platform, article_type)
        user_template = self._build_user_template(article_type)

        return system_prompt, user_template

    def _build_system_prompt(
        self,
        platform: dict,
        article_type: dict,
    ) -> str:
        prompt_parts = [
            f"你是一位专注于{platform['display_name']}平台的自媒体写作专家。",
            f"你擅长创作{article_type['display_name']}类型的文章。",
            "",
            "平台特征:",
            f"- 字数范围: {platform['min_length']}-{platform['max_length']}字",
            f"- 风格特点: {', '.join(platform['style_features'])}",
            f"- 内容结构: {platform['structure_template']}",
            "",
            "写作要求:",
        ]

        for tip in platform.get("tips", []):
            prompt_parts.append(f"- {tip}")

        prompt_parts.extend([
            "",
            "文章类型规范:",
            f"- 类型定义: {article_type['description']}",
            f"- 适用结构: {article_type['structure']}",
            f"- 语言风格: {article_type['tone']}",
            "",
            "写作技巧:",
        ])

        for tip in article_type.get("writing_tips", []):
            prompt_parts.append(f"- {tip}")

        if article_type.get("need_references"):
            prompt_parts.extend([
                "",
                "注意:此类文章需要有参考资料或数据支撑，请在结尾添加参考资料章节。",
            ])

        return "\n".join(prompt_parts)

    def _build_user_template(self, article_type: dict) -> str:
        template = """请根据以下信息，创作一篇{length}字的{article_type}文章。

主题: {topic}
关键词: {keywords}
平台: {platform}

{materials_section}

要求:
- 结构: {structure}
- 风格: {tone}
- 字数: {length}字

写作要点:
{writing_tips}

请直接输出Markdown格式的文章内容。"""

        tips_text = "\n".join([f"- {t}" for t in article_type.get("writing_tips", [])])

        return template.format(
            article_type=article_type["display_name"],
            topic="{topic}",
            keywords="{keywords}",
            platform="{platform}",
            materials_section="{materials}",
            structure=article_type["structure"],
            tone=article_type["tone"],
            length="{length}",
            writing_tips=tips_text,
        )

    def get_available_combinations(self) -> list[dict]:
        combinations = []
        for p in list_platform_ids():
            for t in list_article_type_ids():
                combinations.append({
                    "platform_id": p,
                    "article_type_id": t,
                    "display_name": f"{get_platform(p)['display_name']} + {get_article_type(t)['display_name']}",
                })
        return combinations


def create_agent(platform_id: str, article_type_id: str) -> tuple[str, str]:
    factory = AgentFactory()
    return factory.create_agent(platform_id, article_type_id)


def get_combinations() -> list[dict]:
    factory = AgentFactory()
    return factory.get_available_combinations()


if __name__ == "__main__":
    system, user = create_agent("zhihu", "essay")
    print("=== System Prompt ===")
    print(system)
    print("\n=== User Template ===")
    print(user)