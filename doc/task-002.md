# 002-SearXNG Search Skill构建

## 背景
Agent需要能够搜索热点素材，需要构建SearXNG Search Skill供Agent调用。

## 目标
1. 创建skills/searchng/目录结构
2. 创建skill.md定义Skill描述和接口
3. 实现search.py封装SearXNG API
4. 支持作为LangGraph Tool调用

## 验收标准
- [ ] skills/searchng/skill.md包含完整Skill定义
- [ ] skills/searchng/search.py可独立调用
- [ ] 返回格式包含title/url/content
- [ ] 可集成到LangGraph作为Tool