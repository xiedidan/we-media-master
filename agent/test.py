from agent.state import SearchResult
from skills.searchng.search import search as search_skill


def search_node(state: dict) -> dict:
    topic = state.get("topic", "")
    keywords = state.get("keywords", [])
    
    query = " ".join(keywords) if keywords else topic
    
    results = search_skill(query, num_results=5)
    
    search_results = [
        {"title": r["title"], "url": r["url"], "content": r.get("content", "")}
        for r in results
    ]
    
    return {
        "search_results": search_results,
    }


def write_node(state: dict) -> dict:
    return {
        "article": "# 测试文章\n\n这是从任务003 LangGraph工作流的测试输出。",
    }


def run_simple(topic: str, keywords: list = None) -> dict:
    state = {
        "topic": topic,
        "keywords": keywords or [],
        "search_results": [],
        "article": "",
        "error": None,
    }
    
    state = search_node(state)
    state = write_node(state)
    
    return state


if __name__ == "__main__":
    result = run_simple("人工智能", ["AI"])
    print("Search results:", len(result.get("search_results", [])))
    print("Article:", result.get("article", "")[:100])