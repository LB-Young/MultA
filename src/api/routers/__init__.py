"""API 路由"""
from .health import router as health_router
from .documents import router as documents_router
from .chunks import router as chunks_router
from .rag import router as rag_router
from .agent import router as agent_router

__all__ = [
    "health_router",
    "documents_router",
    "chunks_router",
    "rag_router",
    "agent_router",
]
