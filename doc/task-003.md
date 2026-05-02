# 003-LangGraph Agent工作流构建

## 背景
使用LangGraph构建Agent工作流，协调搜索和写作流程。

## 目标
1. 定义Agent状态结构
2. 构建搜索素材节点
3. 构建文章生成节点
4. 定义工作流边和条件分支

## 验收标准
- [ ] agent/graph.py定义完整工作流
- [ ] 工作流包含search和write两个关键节点
- [ ] 支持从main调用