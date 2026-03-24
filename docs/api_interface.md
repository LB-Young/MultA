# 外部模型服务接口规范

本系统支持接入五类外部模型服务：Embedding（向量化）、LLM（大语言模型）、图片 OCR、音频转文本、CAD 解析。

所有接口格式均以 **OpenAI API 标准**为基准，可直接对接 OpenAI、Azure OpenAI、阿里云百炼、腾讯混元、字节火山引擎等提供 OpenAI 兼容接口的云服务商，无需修改代码。

---

## 通用说明

### 鉴权方式

所有外部 API 均通过 `Authorization` 请求头传入 API 密钥：

```
Authorization: Bearer <your_api_key>
```

若未配置密钥，则不携带该请求头。

### 错误处理

系统仅处理 HTTP 状态码 `200` 的响应，非 200 响应将记录错误并跳过对应文件。

---

## 一、Embedding API（向量化服务）

**用途：** 将文本切片转换为浮点数向量，写入向量数据库。

**对应 OpenAI 接口：** `POST /v1/embeddings`

**兼容云服务商：**
- OpenAI、Azure OpenAI
- 阿里云百炼（`POST /compatible-mode/v1/embeddings`）
- 腾讯混元、字节火山引擎等 OpenAI 兼容接口

### 请求

- **方法：** `POST`
- **Content-Type：** `application/json`

```json
{
  "input": "需要向量化的文本内容",
  "model": "text-embedding-ada-002"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `input` | string | 待向量化的文本，单次调用对应一个切片 |
| `model` | string | 模型名称，从 `config.yaml` 的 `embedding.model` 读取 |

### 响应

**标准格式（OpenAI 格式，优先解析）：**

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023064255, -0.009327292, 0.015797347, "..."],
      "index": 0
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

**简化格式（兼容，次优先）：**

```json
{
  "embedding": [0.0023064255, -0.009327292, "..."]
}
```

或：

```json
{
  "vector": [0.0023064255, -0.009327292, "..."]
}
```

解析优先级：`data[0].embedding` → `embedding` → `vector`

> **注意：** 向量维度须与向量数据库集合的维度一致。系统默认 `bge-large-zh-v1.5`，维度为 **1024**；OpenAI `text-embedding-ada-002` 维度为 **1536**；`text-embedding-3-small` 为 **1536**；`text-embedding-3-large` 为 **3072**。更换模型时需删除旧集合并重建。

---

## 二、LLM API（大语言模型服务）

**用途：** 基于检索到的文档上下文生成问题的答案。

**对应 OpenAI 接口：** `POST /v1/chat/completions`

**兼容云服务商：**
- OpenAI、Azure OpenAI
- 阿里云百炼（通义千问）
- 腾讯混元、字节火山引擎豆包
- Ollama（`/api/chat`，本地部署）
- vLLM（`/v1/chat/completions`，本地部署）
- FastChat、LM Studio 等兼容 OpenAI 格式的推理框架

### 请求

- **方法：** `POST`
- **Content-Type：** `application/json`

```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "你是企业知识库智能助手。请根据以下检索到的文档内容回答用户的问题。\n\n## 检索到的文档内容：\n[文档 1]\n...\n\n---\n\n[文档 2]\n...\n\n## 用户问题：\n用户输入的问题\n\n## 回答："
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型名称，从 `config.yaml` 的 `llm.model` 读取 |
| `messages` | array | 消息列表，固定为单条 `user` 角色消息，内容为拼好的提示词 |
| `messages[].role` | string | 固定为 `"user"` |
| `messages[].content` | string | 包含检索上下文与用户问题的完整提示词 |
| `temperature` | float | 生成温度，从 `config.yaml` 的 `llm.temperature` 读取，默认 `0.7` |
| `max_tokens` | int | 最大生成 token 数，从 `config.yaml` 的 `llm.max_tokens` 读取，默认 `2000` |

### 响应

**标准格式（OpenAI 格式，优先解析）：**

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "根据文档内容，答案是..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 512,
    "completion_tokens": 128,
    "total_tokens": 640
  }
}
```

**简化格式（兼容，次优先）：**

```json
{
  "content": "根据文档内容，答案是..."
}
```

解析优先级：`choices[0].message.content` → `content`

---

## 三、图片 OCR API

**用途：** 对图片文件（jpg、jpeg、png、gif、bmp）进行文字识别。

**说明：** 主流云服务商的图片 OCR 接口格式差异较大（如 Azure 使用 URL 或 base64、百度 OCR 使用 base64），建议通过自建适配层将本系统的 multipart 格式转换为对应云服务商格式，或直接部署支持 multipart 上传的 OCR 服务。

### 请求

- **方法：** `POST`
- **Content-Type：** `multipart/form-data`
- **超时：** 60 秒

```
file=<图片文件二进制内容>
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | binary | 图片文件原始内容，带文件名 |

### 响应

```json
{
  "text": "图片中识别出的文字内容"
}
```

或：

```json
{
  "content": "图片中识别出的文字内容"
}
```

解析优先级：`text` → `content`

---

## 四、音频转文本 API（ASR）

**用途：** 对音频文件（mp3、wav、m4a、aac）进行语音识别。

**对应 OpenAI 接口：** `POST /v1/audio/transcriptions`

**兼容云服务商：**
- OpenAI Whisper API
- Azure OpenAI Whisper
- 阿里云语音识别（需确认接口格式）
- 本地部署的 Whisper 服务（faster-whisper、whisper.cpp 等）

### 请求

- **方法：** `POST`
- **Content-Type：** `multipart/form-data`
- **超时：** 120 秒

```
file=<音频文件二进制内容，带文件名>
model=whisper-1
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | binary | 音频文件原始内容，带原始文件名 |
| `model` | string | 模型名称，从 `config.yaml` 的 `external_extractors.audio.model` 读取，默认 `whisper-1` |

### 响应

```json
{
  "text": "音频中转录出的文字内容"
}
```

或：

```json
{
  "content": "音频中转录出的文字内容"
}
```

解析优先级：`text` → `content`

> OpenAI Whisper 标准响应即为 `{"text": "..."}` 格式，可直接对接。

---

## 五、CAD 解析 API

**用途：** 对 CAD 图纸文件（dwg、dxf）进行解析，返回文字标注或结构化描述。

**说明：** 目前无统一的云服务商标准，通常需要自建或使用专业的 CAD 解析服务。

### 请求

- **方法：** `POST`
- **Content-Type：** `multipart/form-data`
- **超时：** 120 秒

```
file=<CAD文件二进制内容>
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | binary | CAD 文件原始内容 |

### 响应

```json
{
  "text": "图纸中提取的文字标注、图层说明、零件信息等"
}
```

或：

```json
{
  "content": "图纸中提取的文字标注、图层说明、零件信息等"
}
```

解析优先级：`text` → `content`

---

## 接口汇总

| 服务 | OpenAI 对标接口 | 请求方式 | 关键入参 | 出参解析路径 |
|------|----------------|----------|----------|-------------|
| Embedding | `POST /v1/embeddings` | JSON | `input`, `model` | `data[0].embedding` → `embedding` → `vector` |
| LLM | `POST /v1/chat/completions` | JSON | `messages`, `model`, `temperature`, `max_tokens` | `choices[0].message.content` → `content` |
| 图片 OCR | 无统一标准 | multipart | `file` | `text` → `content` |
| 音频 ASR | `POST /v1/audio/transcriptions` | multipart | `file`, `model` | `text` → `content` |
| CAD 解析 | 无统一标准 | multipart | `file` | `text` → `content` |

---

## 配置方式

在 `config.yaml` 中填写对应 API 地址和密钥，或在页面左侧侧边栏实时配置：

```yaml
api:
  embedding:
    type: "external"
    url: "https://api.openai.com/v1/embeddings"
    key: "sk-xxxx"

  llm:
    type: "external"
    url: "https://api.openai.com/v1/chat/completions"
    key: "sk-xxxx"

embedding:
  model: "text-embedding-ada-002"  # 对应 embedding 请求中的 model 字段

llm:
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

external_extractors:
  image:
    url: "http://your-ocr-service/ocr"
    key: ""
  audio:
    url: "https://api.openai.com/v1/audio/transcriptions"
    key: "sk-xxxx"
    model: "whisper-1"           # 对应 ASR 请求中的 model 字段
  cad:
    url: "http://your-cad-service/parse"
    key: ""
```

### 接入常见云服务商示例

| 云服务商 | Embedding URL | LLM URL |
|----------|--------------|---------|
| OpenAI | `https://api.openai.com/v1/embeddings` | `https://api.openai.com/v1/chat/completions` |
| Azure OpenAI | `https://{resource}.openai.azure.com/openai/deployments/{deploy}/embeddings?api-version=2024-02-01` | `https://{resource}.openai.azure.com/openai/deployments/{deploy}/chat/completions?api-version=2024-02-01` |
| 阿里云百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings` | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |
| 字节火山引擎 | `https://ark.cn-beijing.volces.com/api/v3/embeddings` | `https://ark.cn-beijing.volces.com/api/v3/chat/completions` |
| Ollama（本地） | 不支持 OpenAI embedding 格式，需自建适配 | `http://localhost:11434/v1/chat/completions` |
| vLLM（本地） | `http://localhost:8000/v1/embeddings` | `http://localhost:8000/v1/chat/completions` |
