"""Agent 路由（直调 LLM）。"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import get_agent_service
from src.application.schemas.agent import AgentQueryRequest, AgentQueryResponse
from src.application.services import AgentService
from src.domain.entities.query import ConversationSession
from src.infrastructure.logging.setup import get_logger, LogContext
from src.infrastructure.storage.session_storage import get_agent_session_repository

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = get_logger(__name__)


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[dict]


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions():
    repo = get_agent_session_repository()
    sessions = repo.list_sessions(limit=50)
    return [
        SessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages),
        )
        for s in sessions
    ]


@router.post("/sessions", response_model=SessionResponse)
async def create_session(title: Optional[str] = None):
    repo = get_agent_session_repository()
    session = ConversationSession(
        id=str(uuid4()),
        title=title or "新对话",
    )
    repo.create_session(session)
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    repo = get_agent_session_repository()
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in session.messages
        ],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    repo = get_agent_session_repository()
    if not repo.delete_session(session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "已删除", "session_id": session_id}


@router.patch("/sessions/{session_id}")
async def rename_session(session_id: str, body: dict):
    repo = get_agent_session_repository()
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    if "title" in body:
        session.title = body["title"]
        repo.update_session(session)
    return {"message": "已更新", "title": session.title}


@router.post("/query", response_model=AgentQueryResponse)
async def query(
    request: AgentQueryRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """Agent 直答：会话编排在路由，模型调用在 AgentService。"""
    with LogContext():
        try:
            response = await agent_service.query_with_history(request)
            repo = get_agent_session_repository()
            if request.session_id:
                session = repo.get_session(request.session_id)
                if session:
                    session.add_user_message(request.text)
                    session.add_assistant_message(response.answer)
                    if len(session.messages) == 2:
                        session.title = request.text[:20] + ("..." if len(request.text) > 20 else "")
                    repo.update_session(session)
                    response.session_id = session.id
            return response
        except Exception as e:
            logger.error(f"Agent 查询失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
