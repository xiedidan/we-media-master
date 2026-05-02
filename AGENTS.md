# 项目规则文档

## 1. 项目简介

- **项目名称**: 自媒体文章创作大师 (we-media-master)
- **项目类型**: AI Agent Web应用
- **核心功能**: 辅助用户完成自媒体长文写作，支持热点素材收集和Markdown输出
- **目标用户**: 自媒体创作者、公众号运营者、内容创业者

## 2. 项目和技术核心决策

### 2.1 技术选型
- **Agent框架**: LangGraph (多模型支持，可扩展性强)
- **前端**: Streamlit (快速原型开发，交互友好)
- **后端**: Python + FastAPI
- **模型**: Ollama (支持本地部署)
- **搜索**: SearXNG (自托管，免费)

### 2.2 开发模式
- **虚拟环境**: venv (Python虚拟环境管理)
- **数据库**: SQLite (轻量级，本地存储)
- **迭代方式**: 快速原型 → Eval评估 → 迭代优化
- **发布周期**: 每周交付一个新版本

### 2.3 MVP范围
- 长文写作 (1500-5000字)
- Markdown格式输出
- 热点素材收集
- MVP不使用RAG，后续需要再加

## 3. 目录规范

### 3.1 项目目录结构
```
we-media-master/
├── app/                        # Streamlit前端应用
│   └── app.py                  # 主应用入口
├── agent/                      # Agent核心逻辑
│   ├── __init__.py
│   ├── graph.py                # LangGraph工作流定义
│   ├── nodes.py                # Agent节点实现
│   └── tools.py                # Agent工具(搜索等)
├── skills/                    # Agent技能模块
│   └── searchng/              # SearXNG搜索Skill
│       ├── __init__.py
│       ├── skill.md
│       └── search.py
├── backend/                    # 后端服务
│   ├── __init__.py
│   ├── api.py                  # FastAPI路由
│   └── models.py               # 数据模型
├── services/                   # 外部服务
│   ├── __init__.py
│   ├── search.py                # 搜索服务(SearXNG封装)
│   └── llm.py                  # LLM服务
├── utils/                      # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── eval/                       # 评估测试脚本
│   └── test_v1.py
├── config/                     # 配置文件
│   ├── settings.yml
│   └── prompts.yml
├── KANBAN.md                   # 项目看板
├── doc/                        # 任务详情目录
│   └── task-xxx.md
├── requirements.txt
└── docker-compose.yml
```

### 3.2 模块职责
| 目录 | 职责 |
|-----|------|
| app/ | Streamlit UI界面，用户交互入口 |
| agent/ | LangGraph工作流，Agent逻辑核心 |
| skills/ | Agent技能模块(SearXNG搜索等) |
| backend/ | FastAPI后端，API接口(如需要) |
| services/ | 外部服务封装(搜索、LLM) |
| config/ | 配置文件 |
| doc/ | 任务文档 |

### 3.3 Skill规范

#### 3.3.1 Skill目录结构
```
skills/
├── __init__.py
├── searchng/               # 搜索Skill
│   ├── __init__.py
│   ├── skill.md            # Skill定义
│   └── search.py          # Skill实现
└── ...
```

#### 3.3.2 Skill格式
- `skill.md`: Skill的描述、输入输出格式
- `search.py`: 具体实现

### 3.4 Eval评估规范

#### 3.4.1 Eval流程
```
开发完成 → 自评 → 修复 → 合并main → 标记版本
```

#### 3.4.2 评估维度
- **功能测试**: 输入主题 → 生成文章 → Markdown输出
- **质量评估**: 文章结构、字数、风格
- **格式验证**: Markdown语法正确，可复制到公众号

## 4. 文档规范

### 4.1 文档结构
```
we-media-master/
├── KANBAN.md                 # 项目看板（任务总览）
├── doc/                      # 任务详情目录
│   ├── task-001-xxx.md       # 任务详情
│   ├── task-002-xxx.md
│   └── ...
└── ...
```

### 4.2 KANBAN.md格式
```markdown
# 项目看板

## 待处理
- [ ] 任务名称 @负责人 @(优先级) 

## 处理中
- [ ] 任务名称 @负责人 @(优先级) - 开始:YYYY-MM-DD

## 已完成
- [x] 任务名称 @负责人 @(优先级) - 完成:YYYY-MM-DD
```

### 4.3 看板操作规范

#### 4.3.1 任务流转流程
```
待处理 →认领→ 处理中 → 完成 → 合并main
```

#### 4.3.2 任务认领规则
1. 从"待处理"移动到"处理中"即视为认领
2. 格式：`- [ ] 任务名称 @负责人 @(优先级)`
3. `@负责人`可填Agent名（如@agent-1）或具体人员

#### 4.3.3 多Agent并行开发规则
1. 每个Agent从main创建自己的feature分支：`feature/agent名-任务名`
2. Agent完成任务后，PR到main前需要在KANBAN中更新状态
3. 任务完成后标记为`[x]`并注明完成日期

#### 4.3.4 Git合并冲突处理
1. 合并前先拉取最新main：`git pull origin main`
2. 如有冲突，Agent解决自身代码冲突
3. 公共文件（如KANBAN.md、doc/）冲突由主协调人处理

### 4.4 任务详情格式 (doc/task-xxx.md)
```markdown
# 任务名称

## 背景
(任务背景和目的)

## 目标
(具体要达成什么)

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 实施记录
(实施过程中的记录和发现)
```

## 5. 研发和部署方式

### 5.1 Git分支管理
- `main`: 主分支，保持稳定可运行
- `feature/*`: 功能开发分支
- `fix/*`: 修复分支

### 5.2 开发流程
1. 从main创建feature分支
2. 在doc/创建任务文档
3. 实现功能
4. 自测通过后合并到main
5. 标记版本号

### 5.3 版本命名
- 格式: v0.1.0 (MVP) → v0.2.0 → ...
- 每周发版

### 5.4 部署方式
- 本地运行: `streamlit run app/app.py`
- Docker部署 (可选)