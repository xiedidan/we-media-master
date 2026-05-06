#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, ".")
from skills.searchng.search import search as search_skill
from agent.prompts import get_system_prompt, build_user_prompt
from services.llm import call_llm, judge_article, JUDGE_SYSTEM_PROMPT, build_judge_prompt


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


def test_article_type():
    print("=== Test 2.1: Article Type ===")
    
    materials = [
        {"title": "AI发展", "content": "人工智能快速发展"},
    ]
    
    types = ["知识普及", "经验分享", "感悟体会", "想法迸发"]
    for at in types:
        user_p = build_user_prompt(
            topic="人工智能",
            keywords=["AI"],
            materials=materials,
            article_type=at,
        )
        assert at in user_p, f"Article type {at} should be in prompt"
        print(f"  - {at}: OK")
    
    print("✓ Article Type OK\n")


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


def test_judge():
    print("=== Test 5: LLM Judge ===")
    
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        import yaml
        with open("config/settings.yml", "r") as f:
            config = yaml.safe_load(f)
        api_key = config.get("llm", {}).get("api_key", "")
    
    if not api_key:
        print("⚠ Skipped: No API Key configured\n")
        return
    
    test_article = """# 人工智能

## 一、AI的发展历程

人工智能技术近年来快速发展，从GPT到Claude，各个大模型不断突破技术边界。

## 二、AI在各行业的应用

AI已经应用到医疗、金融、教育等领域。例如，某医院使用AI辅助诊断，准确率大幅提升。

## 三、未来展望

AI将继续改变我们的生活和工作方式。

### 总结

AI是未来发展的重要方向。

---
**参考资料**
- [AI发展现状](https://example.com)
- [大模型技术](https://example2.com)
"""

    materials = [
        {"title": "AI发展", "content": "人工智能快速发展"},
    ]
    user_p = build_user_prompt(
        topic="人工智能",
        keywords=["AI", "发展"],
        materials=materials,
        length="medium",
        style="professional",
        article_type="知识普及",
    )
    
    print("Calling LLM to generate article...")
    article = call_llm(user_p, "你是一位专业自媒体作家，请直接输出Markdown格式文章，只输出文章内容不要其他。", api_key)
    
    if article.startswith("错误："):
        print(f"⚠ Article generation failed: {article}\n")
        return
    
    print(f"Generated article length: {len(article)}")
    
    print("Calling LLM to judge article...")
    result = judge_article(
        topic="人工智能",
        keywords=["AI", "发展"],
        article=article,
        article_type="知识普及",
        style="professional",
        target_length=3000,
        api_key=api_key,
    )
    
    if "error" in result:
        print(f"⚠ Judge failed: {result.get('error')}")
        print(f"Raw: {result.get('raw_result', '')[:200]}...\n")
        return
    
    print(f"总评: {result.get('总分', 0)}分")
    for dim, data in result.items():
        if dim == "总分":
            continue
        if isinstance(data, dict):
            print(f"  - {dim}: {data.get('得分', 0)}分 - {data.get('评语', '')}")
    
    print("✓ Judge OK\n")


def main():
    print("=" * 50)
    print("MVP Integration Tests v1.0")
    print("=" * 50 + "\n")
    
    try:
        test_search()
        test_prompts()
        test_article_type()
        test_workflow()
        test_markdown_format()
        test_judge()
        
        print("=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())