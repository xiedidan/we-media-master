from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    content: str = ""


class AgentState(TypedDict):
    topic: str
    keywords: List[str]
    search_results: List[SearchResult]
    article: str
    error: Optional[str]