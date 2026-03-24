# 企业知识库 RAG 系统 - 文件切片可视化模块

**版本：** V1.0 | **日期：** 2026年3月16日

---

## 一、项目概述

基于 Streamlit 的企业本地知识库 RAG 系统，支持多文件上传、智能切片、可视化查看和问答功能。

## 二、技术栈

- **后端 + 前端**：Streamlit（纯 Python）
- **文件处理**：python-docx, openpyxl, python-pptx, PyPDF2, pillow
- **向量数据库**：可配置（Chroma / Qdrant / Milvus），默认 Qdrant

## 三、配置管理

### 3.1 配置文件结构 (config.yaml)

```yaml
# API 配置
api:
  embedding:
    type: "local"  # local / external
    url: ""  # 外部 API 地址
    key: ""  # API 密钥

  llm:
    type: "local"
    url: ""
    key: ""

  reranker:
    type: "local"
    url: ""
    key: ""

# 文本提取配置
text_extractors:
  # 按文件后缀配置提取器
  txt: "builtin"
  md: "builtin"
  json: "builtin"
  docx: "builtin"
  xlsx: "builtin"
  pptx: "builtin"
  pdf: "builtin"
  jpg: "external"
  jpeg: "external"
  png: "external"
  mp3: "external"
  wav: "external"
  dwg: "external"
  dxf: "external"
  # external 表示调用外部 API

# 切片配置
chunking:
  strategy: "fixed_chars"  # fixed_chars / fixed_tokens / semantic
  chunk_size: 500
  overlap: 50

# 向量数据库配置
vector_db:
  type: "qdrant"  # chroma / qdrant / milvus
  host: "localhost"
  port: 6333
  collection_name: "knowledge_base"
```

### 3.2 配置优先级

- 运行时 Streamlit 侧边栏配置 > config.yaml 配置

## 四、模块设计

### 4.1 配置管理模块 (config.py)

- 加载 config.yaml
- 提供配置读取接口
- 支持配置合并（侧边栏覆盖文件配置）

### 4.2 文件上传模块 (upload.py)

- 支持单文件上传（拖拽 + 点击）
- 支持文件夹上传（递归读取子文件夹）
- 文件类型过滤
- 已上传文件列表管理

### 4.3 文本提取模块 (extractor.py)

```python
class TextExtractor:
    # 内置提取器
    def extract_txt(self, file_path) -> str
    def extract_docx(self, file_path) -> str
    def extract_xlsx(self, file_path) -> str
    def extract_pptx(self, file_path) -> str
    def extract_pdf(self, file_path) -> str

    # 外部 API 提取（预留接口）
    def extract_image_via_api(self, file_path) -> str
    def extract_audio_via_api(self, file_path) -> str
    def extract_cad_via_api(self, file_path) -> str

    # 提取入口
    def extract(self, file_path, extractor_type) -> str
```

### 4.4 切片模块 (chunker.py)

```python
class Chunker:
    # 固定字符数切分
    def chunk_by_chars(self, text, chunk_size, overlap) -> List[Chunk]

    # 固定 token 切分
    def chunk_by_tokens(self, text, chunk_size, overlap) -> List[Chunk]

    # 语义切分（调用外部模型）
    def chunk_by_semantic(self, text) -> List[Chunk]

    # 切片入口
    def chunk(self, text, strategy, chunk_size, overlap) -> List[Chunk]
```

### 4.5 向量数据库模块 (vector_store.py)

```python
class VectorStore:
    def __init__(self, config)

    # 初始化
    def init(self)

    # 添加文档
    def add_documents(self, chunks, metadata)

    # 相似性检索
    def search(self, query, top_k) -> List[Result]

    # 删除集合
    def delete_collection(self)
```

### 4.6 问答模块 (qa.py)

```python
class QA:
    def __init__(self, config)

    # 检索相关文档
    def retrieve(self, query, top_k) -> List[Chunk]

    # 生成答案
    def generate(self, query, context) -> str

    # 问答入口
    def answer(self, query) -> Answer
```

## 五、界面设计

### 5.1 整体布局

```
┌─────────────────────────────────────────────────────────────────┐
│                    企业知识库 RAG 系统                           │
├──────────────────────┬──────────────────────────────────────────┤
│                      │  [文件上传]  [切片可视化]  [知识问答]      │
│   侧边栏配置          │──────────────────────────────────────────│
│                      │                                          │
│  ▼ API 配置          │         主内容区域                        │
│    - Embedding API   │                                          │
│    - LLM API         │    (根据选中 Tab 显示不同内容)            │
│    - Reranker API    │                                          │
│                      │                                          │
│  ▼ 文本提取配置      │                                          │
│    - txt: 内置       │                                          │
│    - pdf: 内置       │                                          │
│    - 图片: 外部API   │                                          │
│    - 音频: 外部API   │                                          │
│    - CAD: 外部API    │                                          │
│                      │                                          │
│  ▼ 切片配置          │                                          │
│    - 策略: [下拉选择]│                                          │
│    - 块大小: [输入]  │                                          │
│    - 重叠: [输入]    │                                          │
│                      │                                          │
│  ▼ 向量库配置        │                                          │
│    - 类型: [下拉选择]│                                          │
│    - 连接参数...     │                                          │
│                      │                                          │
└──────────────────────┴──────────────────────────────────────────┘
```

### 5.2 Tab 功能

1. **文件上传**：
   - 单文件上传区域
   - 文件夹上传区域
   - 已上传文件列表
   - "开始处理" 按钮

2. **切片可视化**：
   - 文件选择器
   - 切片列表（序号、内容预览、字符数、位置）
   - 展开查看完整内容

3. **知识问答**：
   - 问题输入框
   - 问答结果（答案 + 来源文档）

## 六、文件结构

```
FileSystem/
├── app.py                 # Streamlit 主应用
├── config.yaml            # 配置文件
├── config.py              # 配置管理模块
├── requirements.txt      # 依赖
├── core/
│   ├── __init__.py
│   ├── extractor.py       # 文本提取模块
│   ├── chunker.py         # 切片模块
│   ├── vector_store.py    # 向量数据库模块
│   └── qa.py             # 问答模块
└── pages/
    ├── __init__.py
    ├── 1_upload.py        # 文件上传页面
    ├── 2_chunks.py        # 切片可视化页面
    └── 3_qa.py            # 知识问答页面
```

## 七、API 占位符说明

以下 API 预留为可配置占位符，用户模型部署完成后填写：

1. **Embedding API** - 文本向量化
2. **LLM API** - 大语言模型生成答案
3. **Reranker API** - 结果重排序
4. **Image OCR API** - 图片文字提取
5. **Audio ASR API** - 音频转文本
6. **CAD Parser API** - CAD 图解析
