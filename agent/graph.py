from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import search_node, write_node, should_search


def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("search", search_node)
    workflow.add_node("write", write_node)
    
    workflow.add_edge(START, "search")
    workflow.add_conditional_edges(
        "search",
        should_search,
        {
            "write": "write",
            "search": "search",
        },
    )
    workflow.add_edge("write", END)
    
    return workflow.compile()


def run_agent(topic: str, keywords: list = None) -> str:
    graph = create_workflow()
    
    result = graph.invoke({
        "topic": topic,
        "keywords": keywords or [],
        "search_results": [],
        "article": "",
        "error": None,
    })
    
    return result.get("article", "")


if __name__ == "__main__":
    article = run_agent("人工智能", ["AI", "发展趋势"])
    print(article)