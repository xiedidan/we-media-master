import os
import yaml
import requests
from typing import List, Optional


def load_config() -> dict:
    config_path = "config/settings.yml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            "llm": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "api_key": "",
                "base_url": "https://api.deepseek.com/v1",
                "temperature": 0.7,
                "max_tokens": 4000,
            }
        }


DEFAULT_SYSTEM_PROMPT = """你是一位专业的自媒体文章写作大师，擅长创作高质量的公众号长文。
写作风格：观点鲜明、结构清晰、语言流畅、贴近读者。

写作规范：
1. 文章长度：1500-5000字
2. 开头：用一个引人入胜的故事或数据切入
3. 主体：3-5个观点，每个观点有案例支撑
4. 结尾：总结+行动号召
5. 使用Markdown格式，#标题、##二级标题、**加粗**
6. 不要使用emoji"""


class LLMClient:
    def __init__(self, api_key: str = None):
        config = load_config()
        llm_config = config.get("llm", {})
        
        self.provider = llm_config.get("provider", "deepseek")
        self.model = llm_config.get("model", "deepseek-v4-flash")
        self.api_key = api_key or llm_config.get("api_key", "")
        self.base_url = llm_config.get("base_url", "https://api.deepseek.com")
        self.temperature = llm_config.get("temperature", 0.7)
        self.max_tokens = llm_config.get("max_tokens", 4000)
        self.thinking = llm_config.get("thinking", False)
    
    def chat(
        self,
        messages: List[dict],
        system_prompt: str = None,
    ) -> str:
        if not self.api_key:
            return "错误：请配置API Key（在config/settings.yml中设置llm.api_key）"
        
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if self.thinking and self.provider == "deepseek":
            data["thinking"] = {"type": "enabled"}
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            return "错误：请求超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return f"错误：API请求失败 - {str(e)}"
        except KeyError:
            return "错误：API响应格式错误"


def call_llm(prompt: str, system_prompt: str = None, api_key: str = None) -> str:
    client = LLMClient(api_key)
    messages = [{"role": "user", "content": prompt}]
    return client.chat(messages, system_prompt)


def validate_api_key(api_key: str, provider: str = "deepseek", model: str = None) -> dict:
    try:
        if provider == "deepseek":
            base_url = "https://api.deepseek.com"
            model = model or "deepseek-v4-flash"
        elif provider == "openai":
            base_url = "https://api.openai.com/v1"
            model = model or "gpt-3.5-turbo"
        else:
            return {"valid": False, "error": f"未知provider: {provider}"}
        
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {"valid": True, "provider": provider, "model": model}
        elif response.status_code == 401:
            return {"valid": False, "error": "API Key无效"}
        elif response.status_code == 403:
            return {"valid": False, "error": "API Key无权限"}
        else:
            return {"valid": False, "error": f"错误码: {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"valid": False, "error": "请求超时"}
    except requests.exceptions.RequestException as e:
        return {"valid": False, "error": f"连接失败: {str(e)}"}


JUDGE_SYSTEM_PROMPT = """你是一位自媒体文章质量评估专家。你需要根据金标准对待评分的文章进行客观公正的评分。

评分原则：
1. 每个维度的评分要有明确的评分依据
2. 评语要简洁、准确
3. 如果文章在某个维度表现优秀，可以给满分
4. 如果文章在某个维度明显不足，要扣分并说明原因

请严格按照指定的输出格式返回JSON结果。"""

JUDGE_PROMPT_TEMPLATE = """你是一位自媒体文章质量评估专家。请对以下文章进行评分。

## 评分维度
1. 用户意图契合 (25分)：是否围绕用户的主题和关键词
2. 文章类型适配 (20分)：是否符合所选文章类型的要求
3. 文风匹配度 (20分)：是否符合选择的文风风格
4. 字数达标 (15分)：在目标字数±20%范围内
5. Markdown格式 (20分)：标题层级正确、格式规范

## 待评分文章
主题：{topic}
关键词：{keywords}
文章类型：{article_type}
文风：{style}
目标字数：{target_length}字

---
{article}
---

## 输出格式
请以JSON格式输出：
{{
  "总分": 0-100,
  "用户意图契合": {{"得分": 0-25, "评语": "简要说明"}},
  "文章类型适配": {{"得分": 0-20, "评语": "简要说明"}},
  "文风匹配度": {{"得分": 0-20, "评语": "简要说明"}},
  "字数达标": {{"得分": 0-15, "评语": "简要说明"}},
  "Markdown格式": {{"得分": 0-20, "评语": "简要说明"}}
}}
"""


def build_judge_prompt(
    topic: str,
    keywords: List[str],
    article: str,
    article_type: str = "知识普及",
    style: str = "professional",
    target_length: int = 3000,
) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        topic=topic,
        keywords=", ".join(keywords) if keywords else "无",
        article=article,
        article_type=article_type,
        style=style,
        target_length=target_length,
    )


def judge_article(
    topic: str,
    keywords: List[str],
    article: str,
    article_type: str = "知识普及",
    style: str = "professional",
    target_length: int = 3000,
    api_key: str = None,
) -> dict:
    prompt = build_judge_prompt(
        topic=topic,
        keywords=keywords,
        article=article,
        article_type=article_type,
        style=style,
        target_length=target_length,
    )
    result = call_llm(prompt, JUDGE_SYSTEM_PROMPT, api_key)
    
    try:
        import json
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        return {"error": "评分结果解析失败", "raw_result": result}
    
    return {"error": "评分失败", "raw_result": result}


if __name__ == "__main__":
    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Model: {client.model}")
    print(f"API Key configured: {bool(client.api_key)}")