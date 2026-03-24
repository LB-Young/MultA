"""Agent 相关 Schema"""
from typing import Optional

from pydantic import BaseModel, Field

from .rag import HistoryMessage


class AgentQueryRequest(BaseModel):
    """Agent 查询请求（仅模型直答，不走检索）。"""

    text: str = Field(..., min_length=1, description="用户输入，任意非空字符串")
    session_id: Optional[str] = Field(None, description="会话 ID，可为空")
    history: list[HistoryMessage] = Field(default_factory=list, description="对话历史，元素结构见 HistoryMessage")


class AgentQueryResponse(BaseModel):
    """Agent 查询响应。"""

    session_id: str
    answer: str
    generation_time: float


__all__ = ["AgentQueryRequest", "AgentQueryResponse"]
