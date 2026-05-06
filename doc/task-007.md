# 007-Eval效果测试体系(LLM评委+金标准)

## 背景
MVP阶段只有基础功能测试，没有效果评估体系。需要引入LLM作为评委，对生成的文章进行主观质量评分。

## 目标
1. 设计评分金标准（结构完整、论据充分、参考资料、字数达标等）
2. 实现LLM评委prompt，让AI评分生成的文章
3. 集成到eval测试框架中

## 验收标准
- [x] 设计4-5个评分维度及对应金标准
- [x] 实现LLM评委prompt
- [x] eval/test_v1.py中增加效果测试函数
- [x] 测试可通过LLM评委评分

## 实施记录
- 2025-05-04: 实现LLM评委功能
- services/llm.py添加judge_article函数
- eval/test_v1.py添加test_judge()测试
- 测试通过：评分结果正常返回JSON格式