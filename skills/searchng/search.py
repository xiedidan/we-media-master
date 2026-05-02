import requests
from typing import List, Dict, Optional
import yaml


def load_config() -> dict:
    config_path = "config/settings.yml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"searxng": {"base_url": "http://localhost:8080", "timeout": 30, "default_results": 5}}


def search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    config = load_config()
    searxng_config = config.get("searxng", {})
    base_url = searxng_config.get("base_url", "http://localhost:8080")
    timeout = searxng_config.get("timeout", 30)

    url = f"{base_url}/search"
    params = {
        "q": query,
        "format": "json",
        "pageno": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:500] if item.get("content") else "",
            })

        return results
    except requests.exceptions.RequestException as e:
        return [{"title": "Error", "url": "", "content": f"Search failed: {str(e)}"}]


def search_sync(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    return search(query, num_results)


if __name__ == "__main__":
    results = search("人工智能", 5)
    for r in results:
        print(f"- {r['title']}")
        print(f"  {r['url']}")