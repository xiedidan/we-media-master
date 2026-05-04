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
        self.model = llm_config.get("model", "deepseek-v4-pro")
        self.api_key = api_key or llm_config.get("api_key", "")
        self.base_url = llm_config.get("base_url", "https://api.deepseek.com/v1")
        self.temperature = llm_config.get("temperature", 0.7)
        self.max_tokens = llm_config.get("max_tokens", 4000)
    
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


if __name__ == "__main__":
    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Model: {client.model}")
    print(f"API Key configured: {bool(client.api_key)}")