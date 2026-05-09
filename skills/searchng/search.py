"""
SearXNG搜索模块
使用本地部署的SearXNG实例进行搜索
"""
import requests
from typing import List, Dict
import yaml
from bs4 import BeautifulSoup


def load_config() -> dict:
    """加载配置文件"""
    config_path = "config/settings.yml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # 默认配置
        return {
            "searxng": {
                "base_url": "http://localhost:18080",
                "timeout": 30,
                "default_results": 5,
                "engines": ""  # 空字符串表示使用所有启用的引擎
            }
        }


def search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    使用SearXNG搜索
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量
        
    Returns:
        搜索结果列表,每个结果包含title、url、content
        
    Raises:
        Exception: 当SearXNG服务不可用时抛出异常
    """
    config = load_config()
    searxng_config = config.get("searxng", {})
    base_url = searxng_config.get("base_url", "http://localhost:18080")
    timeout = searxng_config.get("timeout", 30)
    engines = searxng_config.get("engines", "bing")

    url = f"{base_url}/search"
    
    # 尝试多种搜索策略
    search_queries = [
        query,  # 原始查询
        f'"{query}"',  # 精确匹配
        f"{query} 新闻",  # 新闻相关
    ]
    
    results = []
    last_error = None
    
    for search_query in search_queries:
        params = {
            "q": search_query,
            "format": "html",  # 使用HTML格式
            "pageno": 1,
            "safesearch": 0,
            "language": "zh-CN",
        }
        
        # 只有当engines不为空时才添加engines参数
        if engines:
            params["engines"] = engines

        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                # 解析HTML结果
                soup = BeautifulSoup(response.text, "html.parser")
                
                # SearXNG的结果在article标签中
                for article in soup.select("article.result"):
                    # 标题和链接
                    title_elem = article.select_one("h3 a")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href", "")
                    
                    # 内容摘要
                    content_elem = article.select_one("p.content")
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    if title and content:
                        results.append({
                            "title": title,
                            "url": link,
                            "content": content[:500],  # 限制内容长度
                        })
                        
                        if len(results) >= num_results:
                            break
                
                # 如果获取到足够结果,直接返回
                if len(results) >= num_results:
                    break
            else:
                last_error = f"SearXNG返回状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            last_error = f"SearXNG请求超时(超过{timeout}秒)"
        except requests.exceptions.ConnectionError:
            last_error = "无法连接到SearXNG服务,请确保docker-compose已启动"
        except Exception as e:
            last_error = f"SearXNG搜索出错: {str(e)}"
    
    # 如果没有获取到任何结果,抛出异常
    if not results:
        error_msg = f"SearXNG搜索失败: {last_error}\n"
        error_msg += f"请检查:\n"
        error_msg += f"1. SearXNG服务是否运行: docker ps | grep searxng\n"
        error_msg += f"2. 代理是否正常: curl -x http://127.0.0.1:6478 https://www.bing.com\n"
        error_msg += f"3. SearXNG是否可访问: curl {base_url}\n"
        raise Exception(error_msg)
    
    return results[:num_results]


def search_sync(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """同步搜索接口(兼容旧代码)"""
    return search(query, num_results)


if __name__ == "__main__":
    # 测试搜索功能
    try:
        results = search("人工智能", 5)
        print(f"搜索成功,获取到{len(results)}条结果:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            print(f"   摘要: {r['content'][:100]}...\n")
    except Exception as e:
        print(f"搜索失败: {e}")
