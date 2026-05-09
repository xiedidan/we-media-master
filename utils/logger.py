import os
import json
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional


LOG_DIR = "logs"


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def save_execution_log(
    topic: str,
    keywords: List[str],
    article: str,
    article_type: str,
    style: str,
    length: str,
    material_count: int,
    score: Optional[Dict] = None,
    error: Optional[str] = None,
    provider: str = None,
    model: str = None,
    thinking: bool = None,
    materials: Optional[List[Dict]] = None,
    llm_calls: Optional[List[Dict]] = None,
    user_rating: int = 0,
    user_feedback: str = "",
) -> str:
    ensure_log_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOG_DIR}/{topic[:20]}_{timestamp}.json"
    
    log_data = {
        "timestamp": timestamp,
        "topic": topic,
        "keywords": keywords,
        "article_type": article_type,
        "style": style,
        "length": length,
        "article_length": len(article),
        "error": error,
    }
    
    if provider:
        log_data["provider"] = provider
    if model:
        log_data["model"] = model
    if thinking is not None:
        log_data["thinking"] = thinking
    
    if materials:
        log_data["materials"] = [
            {"title": m.get("title", ""), "url": m.get("url", "")}
            for m in materials[:material_count]
        ]
    
    if llm_calls:
        log_data["llm_calls"] = [
            {
                "call_num": i + 1,
                "input_length": len(c.get("input", "")),
                "output_length": len(c.get("output", "")),
                "error": c.get("error"),
            }
            for i, c in enumerate(llm_calls)
        ]
    
    if score:
        log_data["score"] = score
    
    if user_rating:
        log_data["user_rating"] = user_rating
    if user_feedback:
        log_data["user_feedback"] = user_feedback
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    return filename


def save_llm_call(
    call_num: int,
    input_prompt: str,
    output: str,
    error: Optional[str] = None,
) -> Dict:
    return {
        "call_num": call_num,
        "input": input_prompt[:500] + "..." if len(input_prompt) > 500 else input_prompt,
        "output": output[:500] + "..." if len(output) > 500 else output,
        "error": error,
    }


def list_logs(limit: int = 10) -> List[Dict]:
    ensure_log_dir()
    
    logs = []
    for f in sorted(os.listdir(LOG_DIR), reverse=True):
        if f.endswith(".json"):
            try:
                with open(f"{LOG_DIR}/{f}", "r", encoding="utf-8") as fp:
                    logs.append(json.load(fp))
            except:
                pass
    
    return logs[:limit]


def get_latest_log() -> Optional[Dict]:
    logs = list_logs(1)
    return logs[0] if logs else None


def update_log_rating(timestamp: str, user_rating: int, user_feedback: str = "") -> bool:
    ensure_log_dir()
    
    for f in os.listdir(LOG_DIR):
        if f.endswith(".json") and timestamp in f:
            try:
                with open(f"{LOG_DIR}/{f}", "r", encoding="utf-8") as fp:
                    log_data = json.load(fp)
                
                log_data["user_rating"] = user_rating
                if user_feedback:
                    log_data["user_feedback"] = user_feedback
                
                with open(f"{LOG_DIR}/{f}", "w", encoding="utf-8") as fp:
                    json.dump(log_data, fp, ensure_ascii=False, indent=2)
                
                return True
            except:
                pass
    
    return False