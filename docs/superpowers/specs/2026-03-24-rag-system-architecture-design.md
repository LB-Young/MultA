# 企业知识库 RAG 系统 - 重构架构设计文档

## 项目概述

基于 Streamlit + FastAPI 的企业级知识库检索增强生成（RAG）系统，支持多格式文档上传、智能切片、向量化存储与知识问答。

**重构目标**：
- 全面重建，从项目结构、代码组织、模块划分全面重构
- 确保架构清晰、可维护性高
- 代码质量优先，同时保证开发、用户、性能

**部署场景**：局域网/私有化部署

---

## 架构设计

### 技术选型

| 组件 | 技术栈 | 说明 |
|------|--------|------|
| 后端框架 | FastAPI | REST API 服务 |
| 前端框架 | Streamlit | Web 用户界面 |
| 核心模块 | 插件化架构 | 可扩展的 extractor、chunker、retriever |
| 向量数据库 | Qdrant/Chroma/Milvus | 可配置切换 |
| 日志系统 | loguru | 结构化日志 + trace_id |
| 测试框架 | pytest | 单元测试 + 集成测试 |
| 存储方式 | 文件系统 | 原始文件 + 向量数据库 |

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │    Streamlit UI     │    │       CLI Tools           │ │
│  └──────────┬──────────┘    └──────────────┬────────────┘ │
│             │                              │              │
│             └──────────┬───────────────────┘              │
│                        ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Backend                     │ │
│  │                   (REST API 服务)                      │ │
│  └──────────────────────────┬───────────────────────────┘ │
└──────────────────────────────┼─────────────────────────────┘
                               │
┌──────────────────────────────┼─────────────────────────────┐
│                    Application Layer                       │
│  ┌──────────────────────────▼────────────────────────────┐ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │ │
│  │  │ Upload   │  │ Chunk    │  │ Vector   │  │ RAG  │ │ │
│  │  │ Service  │  │ Service  │  │ Service  │  │Serv. │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘ │ │
│  └──────────────────────────┬───────────────────────────┘ │
└──────────────────────────────┼─────────────────────────────┘
                               │
┌──────────────────────────────┼─────────────────────────────┐
│                      Domain Layer                           │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │  │
│  │  │Document │  │  Chunk  │  │ Vector  │  │  Query  │ │  │
│  │  │ Entity  │  │ Entity  │  │ Entity  │  │ Entity  │ │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Plugin Registry (插件注册中心)            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │  Extractors │  │  Chunkers   │  │  Retrievers  │  │  │
│  │  │  (插件化)   │  │  (插件化)   │  │  (插件化)   │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┼─────────────────────────────┘
                               │
┌──────────────────────────────┼─────────────────────────────┐
│                   Infrastructure Layer                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ File Storage │ │ Vector Store │ │    Logger    │       │
│  │ (本地文件系统)│ │ (Qdrant等)  │ │  (结构化日志)│       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└────────────────────────────────────────────────────────────┘
```

---

## 项目目录结构

```
FileSystem/
├── src/                          # 核心源代码
│   ├── __init__.py
│   ├── api/                      # API 层
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 入口
│   │   ├── routers/
│   │   │   ├── documents.py      # 文档管理 API
│   │   │   ├── chunks.py         # 切片管理 API
│   │   │   └── rag.py            # RAG 问答 API
│   │   └── deps.py               # 依赖注入
│   │
│   ├── application/              # 应用层
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── chunk_service.py
│   │   │   ├── vector_service.py
│   │   │   └── rag_service.py
│   │   └── schemas/              # Pydantic 请求/响应模型
│   │       ├── document.py
│   │       ├── chunk.py
│   │       └── rag.py
│   │
│   ├── domain/                   # 领域层
│   │   ├── __init__.py
│   │   ├── entities/             # 领域实体
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   └── query.py
│   │   ├── repositories/         # 仓储接口
│   │   │   ├── document_repo.py
│   │   │   └── vector_repo.py
│   │   └── plugins/              # 插件化接口
│   │       ├── base.py           # 插件基类
│   │       ├── extractor.py      # 提取器接口
│   │       ├── chunker.py        # 切片器接口
│   │       └── retriever.py      # 检索器接口
│   │
│   ├── infrastructure/           # 基础设施层
│   │   ├── __init__.py
│   │   ├── storage/             # 文件存储
│   │   │   └── file_storage.py
│   │   ├── vector_db/           # 向量数据库
│   │   │   ├── base.py
│   │   │   ├── qdrant.py
│   │   │   ├── chroma.py
│   │   │   └── factory.py
│   │   ├── extractors/          # 提取器实现
│   │   │   ├── builtin/
│   │   │   │   ├── txt.py
│   │   │   │   ├── docx.py
│   │   │   │   ├── pdf.py
│   │   │   │   ├── xlsx.py
│   │   │   │   ├── pptx.py
│   │   │   │   └── markdown.py
│   │   │   └── external/
│   │   │       ├── ocr.py
│   │   │       └── asr.py
│   │   ├── chunkers/            # 切片器实现
│   │   │   ├── fixed_chars.py
│   │   │   ├── fixed_tokens.py
│   │   │   └── semantic.py
│   │   ├── llm/                 # LLM 调用
│   │   │   └── client.py
│   │   ├── embedding/           # Embedding 调用
│   │   │   └── client.py
│   │   ├── reranker/            # Reranker 调用
│   │   │   └── client.py
│   │   └── logging/             # 结构化日志
│   │       └── setup.py
│   │
│   └── cli/                     # CLI 工具
│       ├── __init__.py
│       └── commands.py          # Click 命令
│
├── ui/                          # Streamlit 前端
│   ├── __init__.py
│   ├── app.py                   # Streamlit 主入口
│   ├── pages/
│   │   ├── upload.py
│   │   ├── chunks.py
│   │   └── qa.py
│   └── components/              # UI 组件
│       ├── file_uploader.py
│       └── chat.py
│
├── tests/                       # 测试
│   ├── __init__.py
│   ├── unit/                    # 单元测试
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/             # 集成测试
│   │   └── api/
│   └── conftest.py              # pytest 配置
│
├── config/                      # 配置文件
│   ├── settings.yaml            # 主配置
│   └── logging.yaml             # 日志配置
│
├── logs/                        # 日志目录
├── data/                        # 数据目录
│   ├── uploads/                 # 上传文件
│   └── processed/               # 处理后文件
│
├── pyproject.toml              # 项目配置
├── requirements.txt            # 依赖
├── README.md
└── Makefile                     # 命令行工具
```

---

## 核心设计原则

### 1. 分层 + 插件化
- **Domain 层** 定义接口（Protocol），不依赖具体实现
- **Infrastructure 层** 实现接口，支持插件化注册
- **Plugin Registry** 统一管理所有插件，支持运行时注册

### 2. 配置中心化
```yaml
# config/settings.yaml
api:
  embedding:
    type: local  # local | external
    url: http://localhost:8001/embed
    key: ""
  llm:
    type: local
    url: http://localhost:11434/api/chat
    key: ""

vector_db:
  type: qdrant
  host: localhost
  port: 6333
  collection_name: knowledge_base

chunking:
  strategy: fixed_chars  # fixed_chars | fixed_tokens | semantic
  chunk_size: 500
  overlap: 50
```

### 3. 结构化日志
- 使用 `loguru`
- 请求级别 `trace_id` 串联
- JSON 格式输出到文件
- 分级输出：DEBUG / INFO / WARNING / ERROR / CRITICAL

```python
# 日志格式
{
    "time": "2026-03-24T10:30:00",
    "level": "INFO",
    "trace_id": "abc123",
    "module": "api.documents",
    "message": "Document uploaded",
    "extra": {"filename": "test.pdf", "size": 1024}
}
```

### 4. 统一错误处理
```python
# 异常类体系
FileSystemError (基类)
├── DocumentNotFoundError
├── ExtractionError
├── ChunkingError
├── VectorizationError
└── RAGError
```

### 5. 插件化设计

```python
# 提取器插件接口
class ExtractorPlugin(Protocol):
    name: str
    supported_extensions: list[str]

    def extract(self, file_path: Path) -> str:
        ...

# 切片器插件接口
class ChunkerPlugin(Protocol):
    name: str

    def chunk(self, text: str, **kwargs) -> list[Chunk]:
        ...

# 注册示例
@register_extractor
class PDFExtractor:
    name = "pdf"
    supported_extensions = [".pdf"]
    ...
```

---

## API 设计

### 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/documents/upload` | 上传文档 |
| GET | `/api/v1/documents` | 列出文档 |
| GET | `/api/v1/documents/{id}` | 获取文档详情 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |

### 切片管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/chunks/process/{document_id}` | 处理文档生成切片 |
| GET | `/api/v1/chunks/{document_id}` | 获取文档切片 |
| DELETE | `/api/v1/chunks/{document_id}` | 删除切片 |

### RAG 问答

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/rag/query` | 问答查询 |
| GET | `/api/v1/rag/history/{session_id}` | 获取对话历史 |

---

## 测试策略

### 单元测试（目标覆盖率 80%+）
- Domain 层：实体、插件接口
- Application 层：所有 Service
- Infrastructure 层：存储、向量库、提取器、切片器

### 集成测试
- API 端点测试
- 文件处理流水线测试
- RAG 流水线测试

### 测试工具
- pytest + pytest-asyncio
- pytest-cov 覆盖率统计
- pytest-mock 模拟依赖

---

## 重构分阶段计划

### 阶段 1：架构搭建
1. 创建项目脚手架（目录结构、pyproject.toml、requirements.txt、Makefile）
2. 基础设施层：日志系统、配置文件、异常体系
3. 领域层：实体定义、仓储接口、插件基类
4. API 层：FastAPI 框架搭建、路由定义

### 阶段 2：核心功能重构
1. 文件存储服务
2. 提取器插件（内置 + 外部）
3. 切片器插件
4. 向量数据库适配
5. Embedding / LLM / Reranker 客户端
6. RAG 流水线

### 阶段 3：前端重构
1. Streamlit UI 重构
2. API 客户端封装
3. 页面组件化

### 阶段 4：测试 + 验收
1. 单元测试（目标覆盖率 80%+）
2. 集成测试
3. 功能验收

---

## 验收标准

- [ ] 项目可正常启动（FastAPI + Streamlit）
- [ ] 文档上传、切片、问答核心流程完整
- [ ] 支持的文件格式：txt, md, json, docx, xlsx, pptx, pdf
- [ ] 支持的切片策略：fixed_chars, fixed_tokens, semantic
- [ ] 支持的向量数据库：qdrant, chroma
- [ ] 单元测试覆盖率 >= 80%
- [ ] 所有 API 端点可正常调用
- [ ] 结构化日志正常输出
- [ ] 统一错误处理，友好的错误提示
