"""RAG 相关 Schema"""
from typing import Optional

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    """对话历史消息"""
    role: str = Field(..., description="角色，可选值: user | assistant")
    content: str = Field(..., description="消息内容，任意非空字符串")


class RAGQueryRequest(BaseModel):
    """RAG 查询请求"""
    text: str = Field(..., min_length=1, description="查询文本，任意非空字符串")
    session_id: Optional[str] = Field(None, description="会话 ID，可为空；若传入则使用该会话继续多轮对话")
    history: list[HistoryMessage] = Field(default_factory=list, description="对话历史，元素结构见 HistoryMessage")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量，可选范围: 1~20")
    retrieval_strategy: str = Field(
        default="dense",
        description="召回策略，可选值: dense | sparse | hybrid",
    )
    query_processing_strategy: str = Field(
        default="standard",
        description="查询处理策略，可选值: standard | normalized",
    )
    reranking_strategy: str = Field(
        default="model",
        description="排序策略，可选值: model | identity",
    )
    context_assembly_strategy: str = Field(
        default="standard",
        description="上下文拼接策略，可选值: standard | compact",
    )
    use_rerank: bool = Field(default=False, description="是否使用重排，可选值: true | false")
    filters: dict = Field(default_factory=dict, description="过滤条件，可选值: 任意 JSON 对象；不传则使用空对象")


class RAGQueryResponse(BaseModel):
    """RAG 查询响应"""
    id: str
    session_id: str
    answer: str
    sources: list[dict]
    retrieved_chunks: int
    generation_time: float


__all__ = ["RAGQueryRequest", "RAGQueryResponse", "HistoryMessage"]
