# 010-API配置增强(多模型+key验证)

## 背景
当前API配置功能较弱，只有单模型和简单保存。需要增强配置功能。

## 目标
1. 支持多模型切换（DeepSeek、OpenAI等）
2. 验证API Key有效性
3. 显示API额度（可选）

## 验收标准
- [x] 支持多模型下拉选择
- [x] 保存key时验证有效性
- [x] 无效key给出明确提示

## 实施记录
- 2025-05-04: config/settings.yml添加多模型配置
- services/llm.py添加validate_api_key函数
- app.py添加模型选择下拉框