import yaml
from typing import Dict, Optional, List


def load_prompts() -> dict:
    config_path = "config/prompts.yml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            "system_prompt": "You are a professional content writer.",
            "user_prompt_template": "Write an article about {topic}.",
        }


def get_system_prompt() -> str:
    prompts = load_prompts()
    return prompts.get("system_prompt", "")


def build_user_prompt(
    topic: str,
    keywords: List[str],
    materials: List[dict],
    length: str = "medium",
    style: str = "professional",
    article_type: str = "知识普及",
) -> str:
    prompts = load_prompts()
    template = prompts.get("user_prompt_template", "")
    
    length_map = prompts.get("length_options", {"short": 1500, "medium": 3000, "long": 5000})
    target_length = length_map.get(length, 3000)
    
    materials_text = "\n".join([
        f"- {m['title']}: {m['content'][:200]}"
        for m in materials
    ])
    
    return template.format(
        topic=topic,
        keywords=", ".join(keywords),
        materials=materials_text,
        length=target_length,
        style=style,
        article_type=article_type,
    )


if __name__ == "__main__":
    materials = [
        {"title": "AI发展", "content": "人工智能快速发展..."},
    ]
    user_prompt = build_user_prompt("人工智能", ["AI", "未来"], materials)
    print("System Prompt:")
    print(get_system_prompt()[:200])
    print("\nUser Prompt:")
    print(user_prompt[:500])