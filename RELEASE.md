# MVP v0.1.0 发布说明

## 版本信息
- 版本号：v0.1.0
- 发布日期：2025-05-02
- 状态：✅ 已完成

## 功能概述
自媒体文章创作大师MVP，支持从素材收集到文章生成的一站式服务。

## 核心功能

### 1. 热点素材搜索
- 使用SearXNG搜索引擎（本地部署）
- 支持Bing引擎搜索
- 返回标题、URL、内容摘要

### 2. 长文生成
- 支持1500/3000/5000字三种长度
- 自定义关键词
- 专业/亲切/通俗三种文风

### 3. Markdown输出
- 标准Markdown格式
- 支持一键复制到公众号
- 支持下载.md文件

## 快速开始

### 环境要求
- Python 3.13+
- Docker + Docker Compose

### 启动步骤

#### 1. 启动SearXNG（如果还未启动）
```bash
docker-compose up -d
```

#### 2. 激活虚拟环境
```bash
source venv/bin/activate
```

#### 3. 运行测试
```bash
python eval/test_v1.py
```

#### 4. 启动UI
```bash
streamlit run app/app.py --server.port 9081
```

## 目录结构
```
we-media-master/
├── app/
│   └── app.py              # Streamlit UI
├── agent/
│   ├── graph.py          # LangGraph工作流
│   ├── nodes.py          # 节点定义
│   ├── state.py         # 状态模型
│   └── prompts.py       # 提示词构建
├── skills/
│   └── searchng/       # 搜索技能
│       ├── search.py
│       └── skill.md
├── config/
│   ├── settings.yml     # 应用配置
│   └── prompts.yml    # 提示词配置
├── eval/
│   └── test_v1.py     # 集成测试
├── venv/              # Python虚拟环境
└── docker-compose.yml
```

## 配置说明

### config/settings.yml
```yaml
searxng:
  base_url: "http://localhost:18080"
  timeout: 30
  default_results: 5
  engines: "bing"

app:
  title: "自媒体文章创作大师"
  debug: true
```

### SearXNG配置
- 端口：18080（与原searxng的8080不冲突）
- 代理：192.168.5.112:6478
- 引擎：Bing

## 人工测试清单

### 测试1：搜索功能
1. 启动：`streamlit run app/app.py --server.port 8511`
2. 打开浏览器 http://localhost:8511
3. 输入主题：人工智能
4. 输入关键词：AI, 未来
5. 点击「生成文章」
6. 检查右侧是否有搜索结果

### 测试2：文章生成
1. 检查文章长度是否符合预期
2. 检查Markdown格式是否正确
3. 检查下载按钮是否可用

### 测试3：参数调整
1. 修改文章长度（short/medium/long）
2. 修改文风（professional/friendly/popular）
3. 检查输出变化

## 已知限制
- LLM调用未实现（输出为占位符）
- 其他搜索引擎暂不可用（Google/DuckDuckGo/Brave被封禁）
- 多平台发布未实现

## 待实现功能（v1.1+）
- RSS订阅抓取
- LLM实际调用
- 多平台发布
- RAG/GraphRAG

## 技术栈
- 前端：Streamlit
- Agent框架：LangGraph
- 搜索：SearXNG
- Python：3.13
- 虚拟环境：venv

## 问题反馈
如有问题，请提交Issue：https://github.com/anomalyco/we-media-master/issues