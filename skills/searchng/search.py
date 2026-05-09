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


def search_with_proxy(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    import httpx
    
    query = query.replace(" ", "+")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        client = httpx.Client(proxy="http://127.0.0.1:6478", timeout=20.0, follow_redirects=True, trust_env=False)
        
        search_queries = [
            f'"{query}"',
            query,
        ]
        
        for search_query in search_queries:
            url = f"https://www.google.com/search?q={search_query}&num={num_results}"
            
            try:
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    results = []
                    for div in soup.select("div.g"):
                        title_elem = div.select_one("h3")
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link_elem = div.select_one("a")
                            link = link_elem.get("href", "") if link_elem else ""
                            
                            snippet_elem = div.select_one("div.VwiC3b")
                            content = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            if title and content:
                                results.append({
                                    "title": title,
                                    "url": link,
                                    "content": content[:500],
                                })
                                
                                if len(results) >= num_results:
                                    break
                    
                    if results:
                        client.close()
                        return results
                        
            except Exception:
                continue
        
        client.close()
    except Exception:
        pass
    
    return []


def search_ddg_fallback(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    try:
        from bs4 import BeautifulSoup
        
        proxies = {
            "http://": "http://127.0.0.1:6478",
            "https://": "http://127.0.0.1:6478",
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query, "b": ""}
        
        response = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for result in soup.select("a.result__a"):
                title = result.get_text(strip=True)
                link = result.get("href", "")
                
                snippet_elem = result.find_next("a", class_="result__snippet")
                content = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                if title and content:
                    results.append({
                        "title": title,
                        "url": link,
                        "content": content[:500],
                    })
                    
                    if len(results) >= num_results:
                        break
            
            return results[:num_results]
    except Exception as e:
        return []


def search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    config = load_config()
    searxng_config = config.get("searxng", {})
    base_url = searxng_config.get("base_url", "http://localhost:8080")
    timeout = searxng_config.get("timeout", 30)
    engines = searxng_config.get("engines", "bing")

    url = f"{base_url}/search"
    
    search_queries = [
        f'"{query}"',
        query,
        f"{query} 新闻",
    ]
    
    results = []
    
    for search_query in search_queries:
        params = {
            "q": search_query,
            "format": "html",
            "pageno": 1,
            "engines": engines,
            "safesearch": 0,
        }

        try:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                
                result_items = soup.select("article.result, div.result")
                
                for result in result_items:
                    title_elem = result.select_one("h3 a, a.result__a")
                    content_elem = result.select_one("p.content, a.result__snippet")
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get("href", "")
                        content = content_elem.get_text(strip=True)[:500] if content_elem else ""
                        
                        if title and content:
                            results.append({
                                "title": title,
                                "url": link,
                                "content": content,
                            })
                            
                            if len(results) >= num_results:
                                break
                
                if len(results) >= num_results:
                    break
                    
        except Exception:
            continue
    
    if not results:
        results = search_with_proxy(query, num_results)
    
    if not results:
        results = search_ddg_fallback(query, num_results)
    
    if not results:
        return [{"title": "搜索失败", "url": "", "content": "无法获取搜索结果，请检查网络或SearXNG服务"}]
    
    return results[:num_results]


def search_sync(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    return search(query, num_results)


if __name__ == "__main__":
    results = search("人工智能", 5)
    for r in results:
        print(f"- {r['title']}")
        print(f"  {r['url']}")