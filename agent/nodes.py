from agent.state import AgentState, SearchResult
from skills.searchng.search import search as search_skill
from typing import List


def search_node(state: AgentState) -> AgentState:
    topic = state.get("topic", "")
    keywords = state.get("keywords", [])
    
    query = " ".join(keywords) if keywords else topic
    
    results = search_skill(query, num_results=10)
    
    search_results = [
        SearchResult(title=r["title"], url=r["url"], content=r.get("content", ""))
        for r in results
    ]
    
    return {
        "search_results": search_results,
    }


def write_node(state: AgentState) -> AgentState:
    return {
        "article": "# Placeholder article\n\nArticle generation will be implemented in task-004."
    }


def should_search(state: AgentState) -> str:
    if not state.get("topic"):
        return "write"
    return "search"