"""健康检查和配置路由"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["健康检查"])


class ConfigUpdate(BaseModel):
    """配置更新请求"""
    llm_url: Optional[str] = None
    llm_model: Optional[str] = None
    llm_type: Optional[str] = None
    embedding_url: Optional[str] = None
    embedding_model: Optional[str] = None
    embedding_type: Optional[str] = None
    reranker_url: Optional[str] = None
    reranker_enabled: Optional[bool] = None


# 运行时配置（可被 UI 更新）
RUNTIME_CONFIG = {
    "llm_url": "http://localhost:11434",
    "llm_model": "qwen3:8b",
    "llm_type": "local",
    "embedding_url": "http://localhost:11434",
    "embedding_model": "nomic-embed-text",
    "embedding_type": "local",
    "reranker_url": "http://localhost:8002",
    "reranker_enabled": False,
}


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "filesystem-rag",
        "version": "0.1.0",
    }


@router.get("/health/ready")
async def readiness_check():
    """就绪检查"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/config")
async def get_config():
    """获取当前配置"""
    return RUNTIME_CONFIG


@router.post("/config")
async def update_config(config: ConfigUpdate):
    """更新配置（运行时生效）"""
    global RUNTIME_CONFIG

    if config.llm_url is not None:
        RUNTIME_CONFIG["llm_url"] = config.llm_url
    if config.llm_model is not None:
        RUNTIME_CONFIG["llm_model"] = config.llm_model
    if config.llm_type is not None:
        RUNTIME_CONFIG["llm_type"] = config.llm_type
    if config.embedding_url is not None:
        RUNTIME_CONFIG["embedding_url"] = config.embedding_url
    if config.embedding_model is not None:
        RUNTIME_CONFIG["embedding_model"] = config.embedding_model
    if config.embedding_type is not None:
        RUNTIME_CONFIG["embedding_type"] = config.embedding_type
    if config.reranker_url is not None:
        RUNTIME_CONFIG["reranker_url"] = config.reranker_url
    if config.reranker_enabled is not None:
        RUNTIME_CONFIG["reranker_enabled"] = config.reranker_enabled

    return {"status": "ok", "config": RUNTIME_CONFIG}


def get_runtime_config():
    """获取运行时配置"""
    return RUNTIME_CONFIG
