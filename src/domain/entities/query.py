"""查询领域实体"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    """查询类型"""
    SEMANTIC = "semantic"      # 语义检索
    KEYWORD = "keyword"        # 关键词检索
    HYBRID = "hybrid"          # 混合检索


class Query(BaseModel):
    """查询实体"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    query_type: QueryType = QueryType.SEMANTIC
    session_id: Optional[str] = None
    top_k: int = 5
    filters: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class QueryResult(BaseModel):
    """查询结果"""
    id: str
    query_id: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 统计信息
    retrieved_chunks: int = 0
    generation_time: float = 0.0


class ConversationMessage(BaseModel):
    """对话消息"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: str  # "user" | "assistant"
    content: str
    query_result: Optional[QueryResult] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ConversationSession(BaseModel):
    """对话会话"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "新对话"
    messages: list[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_user_message(self, content: str) -> ConversationMessage:
        """添加用户消息"""
        message = ConversationMessage(
            session_id=self.id,
            role="user",
            content=content,
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def add_assistant_message(
        self, 
        content: str, 
        query_result: Optional[QueryResult] = None
    ) -> ConversationMessage:
        """添加助手消息"""
        message = ConversationMessage(
            session_id=self.id,
            role="assistant",
            content=content,
            query_result=query_result,
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message


class QueryRequest(BaseModel):
    """查询请求"""
    text: str
    session_id: Optional[str] = None
    top_k: int = 5
    retrieval_strategy: str = "dense"
    query_processing_strategy: str = "standard"
    reranking_strategy: str = "model"
    context_assembly_strategy: str = "standard"
    use_rerank: bool = False
    filters: dict = Field(default_factory=dict)


class QueryResponse(BaseModel):
    """查询响应"""
    id: str
    session_id: str
    answer: str
    sources: list[dict] = Field(default_factory=list)
    retrieved_chunks: int
    generation_time: float
    created_at: datetime


__all__ = [
    "Query",
    "QueryType",
    "QueryResult",
    "QueryRequest",
    "QueryResponse",
    "ConversationMessage",
    "ConversationSession",
]
