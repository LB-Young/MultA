"""AgentService 测试"""
import asyncio

from src.application.schemas.agent import AgentQueryRequest
from src.application.services.agent_service import AgentService
from src.application.schemas.rag import HistoryMessage


class _FakeLLMClient:
    def __init__(self):
        self.last_messages = None

    async def chat(self, messages):
        self.last_messages = messages
        return "agent测试回答"


def test_agent_service_query_with_history_uses_llm_and_keeps_session_id():
    llm = _FakeLLMClient()
    service = AgentService(llm_client=llm)
    request = AgentQueryRequest(
        text="你好",
        session_id="agent-session-1",
        history=[HistoryMessage(role="user", content="上一轮问题")],
    )

    response = asyncio.run(service.query_with_history(request))

    assert response.answer == "agent测试回答"
    assert response.session_id == "agent-session-1"
    assert response.generation_time >= 0
    assert llm.last_messages == [
        {"role": "user", "content": "上一轮问题"},
        {"role": "user", "content": "你好"},
    ]
