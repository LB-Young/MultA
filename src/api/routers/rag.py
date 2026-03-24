"""RAG 路由"""
from datetime import datetime
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.services import RAGService
from src.application.schemas.rag import RAGQueryRequest, RAGQueryResponse, HistoryMessage
from src.api.deps import get_rag_service
from src.infrastructure.storage.session_storage import get_session_repository
from src.domain.entities.query import ConversationSession, ConversationMessage
from src.infrastructure.logging.setup import get_logger, LogContext

router = APIRouter(prefix="/rag", tags=["RAG 问答"])
logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════
# 会话管理
# ══════════════════════════════════════════════════════════

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
    """列出所有会话（按更新时间倒序）"""
    repo = get_session_repository()
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
    """创建新会话"""
    repo = get_session_repository()
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
    """获取会话详情（含消息历史）"""
    repo = get_session_repository()
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
    """删除会话"""
    repo = get_session_repository()
    if not repo.delete_session(session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "已删除", "session_id": session_id}


@router.patch("/sessions/{session_id}")
async def rename_session(session_id: str, body: dict):
    """重命名会话"""
    repo = get_session_repository()
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    if "title" in body:
        session.title = body["title"]
        repo.update_session(session)
    return {"message": "已更新", "title": session.title}


# ══════════════════════════════════════════════════════════
# RAG 查询
# ══════════════════════════════════════════════════════════

@router.post("/query", response_model=RAGQueryResponse)
async def query(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """问答查询（支持多轮对话）"""
    with LogContext() as trace:
        try:
            # 多轮：带历史记录
            response = await rag_service.query_with_history(request)

            # 追加消息到会话
            if request.session_id:
                repo = get_session_repository()
                session = repo.get_session(request.session_id)
                if session:
                    session.add_user_message(request.text)
                    session.add_assistant_message(response.answer)
                    # 第一条消息自动生成标题
                    if len(session.messages) == 2:
                        session.title = request.text[:20] + ("..." if len(request.text) > 20 else "")
                    repo.update_session(session)

            return RAGQueryResponse(
                id=response.id,
                session_id=request.session_id or "",
                answer=response.answer,
                sources=response.sources,
                retrieved_chunks=response.retrieved_chunks,
                generation_time=response.generation_time,
            )

        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
