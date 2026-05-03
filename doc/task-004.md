# 004-长文生成提示词设计

## 背景
设计高质量的长文生成提示词，引导LLM生成1500-5000字的自媒体长文。

## 目标
1. 设计system prompt（角色设定和写作规范）
2. 设计userprompt模板（结合素材生成）
3. 支持参数化（主题、风格、长度等）

## 验收标准
- [x] config/prompts.yml包含完整提示词
- [x] agent/prompts.py提示词构建模块
- [x] 支持1500-5000字长度控制

## 实施记录
- 创建config/prompts.yml，包含system prompt和user prompt模板
- 创建agent/prompts.py，提示词构建函数
- 测试通过