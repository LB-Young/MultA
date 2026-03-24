# 企业知识库 RAG 系统

基于 FastAPI + Streamlit 的企业级知识库检索增强生成（RAG）系统，支持多格式文档上传、智能切片、向量化存储与知识问答。

## 特性

- **多格式支持**：支持 txt, md, json, docx, xlsx, pptx, pdf 等常见文档格式
- **智能切片**：支持固定字符、固定 Token、语义切片等多种策略
- **向量检索**：支持 Qdrant、Chroma 等向量数据库
- **RAG 问答**：基于检索增强的问答系统，支持精排重排序
- **结构化日志**：完整的请求追踪和日志记录
- **分层架构**：清晰的分层 + 插件化架构设计

## 技术栈

- **后端**：FastAPI + Pydantic
- **前端**：Streamlit
- **向量数据库**：Qdrant / Chroma
- **日志**：Loguru
- **测试**：Pytest

## 项目结构

```
FileSystem/
├── src/                    # 核心源代码
│   ├── api/               # FastAPI 路由和入口
│   ├── application/       # 应用服务层
│   ├── domain/            # 领域层（实体、仓储、插件）
│   ├── infrastructure/    # 基础设施层
│   └── cli/               # CLI 工具
├── ui/                     # Streamlit 前端
├── tests/                  # 测试
├── config/                 # 配置文件
├── data/                   # 数据目录
└── logs/                   # 日志目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化

```bash
# 初始化数据目录
make setup

# 或者手动初始化
python scripts/setup.py
```

### 3. 启动服务

启动 FastAPI 后端：

```bash
# 开发模式
make dev

# 或者
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

启动 Streamlit 前端：

```bash
# 新开终端
make ui

# 或者
streamlit run ui/app.py --server.fileWatcherType poll
```

### 4. 访问

- FastAPI 文档：http://localhost:8000/docs
- Streamlit UI：http://localhost:8501

## 配置

配置文件位于 `config/settings.yaml`：

```yaml
# API 配置
api:
  embedding:
    type: local
    url: http://localhost:8001/embed
  llm:
    type: local
    url: http://localhost:11434/api/chat
    model: qwen2.5

# 向量数据库配置
vector_db:
  type: qdrant  # qdrant | chroma
  host: localhost
  port: 6333
  collection_name: knowledge_base

# 切片配置
chunking:
  strategy: fixed_chars  # fixed_chars | fixed_tokens
  chunk_size: 500
  overlap: 50
```

## 开发

### 代码检查

```bash
make lint
```

### 运行测试

```bash
# 运行所有测试
make test

# 运行覆盖率报告
make coverage
```

## API 文档

### 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/documents/upload` | 上传文档 |
| GET | `/documents` | 列出文档 |
| GET | `/documents/{id}` | 获取文档详情 |
| DELETE | `/documents/{id}` | 删除文档 |
| POST | `/documents/{id}/process` | 处理文档 |

### RAG 问答

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/rag/query` | 问答查询 |

## CLI 工具

```bash
# 初始化数据目录
python -m src.cli.commands init

# 处理单个文件
python -m src.cli.commands process path/to/file.pdf --chunk-size 500

# 查看系统信息
python -m src.cli.commands info

# 管理向量集合
python -m src.cli.commands collection knowledge_base --recreate
```

## 许可证

MIT License
