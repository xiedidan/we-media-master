#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, ".")
from skills.searchng.search import search as search_skill
from agent.prompts import get_system_prompt, build_user_prompt


def test_search():
    print("=== Test 1: Search ===")
    results = search_skill("人工智能", num_results=3)
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - {r['title'][:40]}")
    assert len(results) > 0, "Search should return results"
    print("✓ Search OK\n")


def test_prompts():
    print("=== Test 2: Prompts ===")
    system_p = get_system_prompt()
    print(f"System prompt length: {len(system_p)}")
    
    materials = [
        {"title": "AI发展", "content": "人工智能快速发展"},
        {"title": "大模型", "content": "大模型技术突破"},
    ]
    user_p = build_user_prompt(
        topic="人工智能",
        keywords=["AI", "未来"],
        materials=materials,
    )
    print(f"User prompt length: {len(user_p)}")
    assert len(system_p) > 0, "System prompt should exist"
    assert len(user_p) > 0, "User prompt should exist"
    print("✓ Prompts OK\n")


def test_workflow():
    print("=== Test 3: Workflow ===")
    from agent.test import search_node, write_node
    
    state = {"topic": "人工智能", "keywords": ["AI"], "search_results": [], "article": "", "error": None}
    state.update(search_node(state))
    state.update(write_node(state))
    
    print(f"Search results: {len(state.get('search_results', []))}")
    print(f"Article length: {len(state.get('article', ''))}")
    assert len(state.get('search_results', [])) > 0, "Should have search results"
    assert len(state.get('article', '')) > 0, "Should have article"
    print("✓ Workflow OK\n")


def test_markdown_format():
    print("=== Test 4: Markdown Format ===")
    article = f"""# 人工智能

## 一、AI的发展

人工智能正在快速发展

## 二、未来的应用

未来AI将应用到各个领域

### 总结

AI改变世界

---
**参考资料**
- [AI发展](https://example.com)
"""
    
    has_h1 = "# 人工智能" in article
    has_h2 = "## " in article
    has_link = "[" in article and "](" in article
    
    print(f"Has H1: {has_h1}")
    print(f"Has H2: {has_h2}")
    print(f"Has link: {has_link}")
    
    assert has_h1, "Should have H1"
    assert has_h2, "Should have H2"
    assert has_link, "Should have link"
    print("✓ Markdown Format OK\n")


def main():
    print("=" * 50)
    print("MVP Integration Tests v1.0")
    print("=" * 50 + "\n")
    
    try:
        test_search()
        test_prompts()
        test_workflow()
        test_markdown_format()
        
        print("=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())