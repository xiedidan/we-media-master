# SearXNG Search Skill

## 技能描述
使用SearXNG元搜索引擎搜索热点素材，获取实时网络信息。

## 输入格式
- `query`: 搜索关键词（必需）
- `num_results`: 返回结果数量（可选，默认5）

## 输出格式
返回JSON格式的搜索结果列表，每个结果包含：
- `title`: 搜索结果标题
- `url`: 网页链接
- `content`: 网页内容摘要

## 使用示例
```python
from skills.searchng import search

results = search("人工智能发展趋势", num_results=10)
for r in results:
    print(f"{r['title']}: {r['url']}")
```