# 016-实现Agent工厂模式

## 背景
需要将平台特征和文章类型组合起来，形成专业的 Agent。

## 目标
实现 Agent 工厂模式，支持平台+类型组合，生成专业化的提示词。

## 验收标准
- [ ] 定义 Agent 配置结构（平台+类型+其他参数）
- [ ] 实现工厂方法，根据配置生成专业 Agent
- [ ] 支持平台特征和文章类型的灵活组合

## 实施记录

### 设计思路

```
Agent = BaseAgent + PlatformConfig + ArticleTypeConfig
```

工厂根据 platform_id + article_type_id 组合，从配置中读取对应的平台特征和文章类型，合并生成专业化的 system prompt。