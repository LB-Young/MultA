"""Agent 服务（模型直答）。"""
import time

from src.application.schemas.agent import AgentQueryRequest, AgentQueryResponse
from src.infrastructure.llm import LLMClient
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class AgentService:
    """Agent 服务：负责组织历史消息并调用 LLM。"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def query_with_history(self, request: AgentQueryRequest) -> AgentQueryResponse:
        start_time = time.time()
        messages = [{"role": m.role, "content": m.content} for m in request.history]
        messages.append({"role": "user", "content": request.text})
        answer = await self.llm_client.chat(messages=messages)
        return AgentQueryResponse(
            session_id=request.session_id or "",
            answer=answer,
            generation_time=time.time() - start_time,
        )


__all__ = ["AgentService"]
