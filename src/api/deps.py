"""依赖注入"""
from functools import lru_cache
from typing import Optional

from src.infrastructure.config import get_settings, Settings
from src.infrastructure.storage.file_storage import FileStorage, JSONDocumentRepository
from src.infrastructure.embedding import EmbeddingClient
from src.infrastructure.llm import LLMClient
from src.infrastructure.reranker import RerankerClient
from src.infrastructure.vector_db import VectorStoreFactory
from src.application.services import DocumentService, ChunkService, RAGService, AgentService
from src.infrastructure.logging.setup import get_logger
from src.api.routers.health import get_runtime_config

logger = get_logger(__name__)

# 全局文档仓储实例（持久化）
_document_repository = None


def get_document_repository() -> JSONDocumentRepository:
    """获取文档仓储（持久化）"""
    global _document_repository
    if _document_repository is None:
        _document_repository = JSONDocumentRepository()
    return _document_repository


# ==================== 配置 ====================

@lru_cache()
def get_settings_cached() -> Settings:
    """获取配置（缓存）"""
    return get_settings()


# ==================== 存储 ====================

def get_file_storage() -> FileStorage:
    """获取文件存储"""
    settings = get_settings_cached()
    return FileStorage(
        upload_dir=settings.storage.upload_dir,
        max_file_size=settings.storage.max_file_size,
    )


# ==================== API 客户端（使用运行时配置） ====================

def get_embedding_client() -> EmbeddingClient:
    """获取 Embedding 客户端（每次请求使用最新配置）"""
    runtime_config = get_runtime_config()
    settings = get_settings_cached()

    return EmbeddingClient(
        api_type=runtime_config.get("embedding_type", settings.api.embedding.type),
        api_url=runtime_config.get("embedding_url", settings.api.embedding.url),
        api_key="",
        model=runtime_config.get("embedding_model", settings.api.embedding.model),
    )


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端（每次请求使用最新配置）"""
    runtime_config = get_runtime_config()
    settings = get_settings_cached()

    return LLMClient(
        api_type=runtime_config.get("llm_type", settings.api.llm.type),
        api_url=runtime_config.get("llm_url", settings.api.llm.url),
        api_key="",
        model=runtime_config.get("llm_model", settings.api.llm.model),
        max_tokens=settings.api.llm.max_tokens,
        temperature=settings.api.llm.temperature,
    )


def get_reranker_client() -> Optional[RerankerClient]:
    """获取 Reranker 客户端"""
    runtime_config = get_runtime_config()
    settings = get_settings_cached()

    if not runtime_config.get("reranker_enabled", False):
        return None

    return RerankerClient(
        api_type="local",
        api_url=runtime_config.get("reranker_url", settings.api.reranker.url),
        api_key="",
        model=settings.api.reranker.model,
    )


# ==================== 服务 ====================

def get_document_service() -> DocumentService:
    """获取文档服务"""
    return DocumentService(
        storage=get_file_storage(),
        repository=get_document_repository(),
    )


def get_chunk_service() -> ChunkService:
    """获取切片服务"""
    return ChunkService(
        document_service=get_document_service(),
        embedding_client=get_embedding_client(),
    )


def get_rag_service() -> RAGService:
    """获取 RAG 服务"""
    return RAGService(
        embedding_client=get_embedding_client(),
        llm_client=get_llm_client(),
        reranker_client=get_reranker_client(),
    )


def get_agent_service() -> AgentService:
    """获取 Agent 服务"""
    return AgentService(
        llm_client=get_llm_client(),
    )


# ==================== 初始化 ====================

async def init_vector_store() -> None:
    """初始化向量数据库（自动检测 embedding 维度）"""
    settings = get_settings_cached()

    # 自动检测 embedding 维度，避免 vector_size 不匹配
    try:
        embedding_client = get_embedding_client()
        actual_vector_size = await embedding_client.get_dimension()
        logger.info(f"检测到 embedding 维度: {actual_vector_size}")
    except Exception as e:
        actual_vector_size = settings.vector_db.vector_size
        logger.warning(f"无法检测 embedding 维度，使用配置值: {actual_vector_size} ({e})")

    VectorStoreFactory.initialize({
        "type": settings.vector_db.type,
        "host": settings.vector_db.host,
        "port": settings.vector_db.port,
        "collection_name": settings.vector_db.collection_name,
        "vector_size": actual_vector_size,
        "distance": settings.vector_db.distance,
    })

    store = VectorStoreFactory.get_store(settings.vector_db.collection_name)
    await store.initialize()

    # 确保集合存在
    await VectorStoreFactory.ensure_collection(
        settings.vector_db.collection_name,
        actual_vector_size,
    )

    logger.info(f"向量数据库初始化完成（维度: {actual_vector_size}）")


__all__ = [
    "get_settings_cached",
    "get_file_storage",
    "get_document_repository",
    "get_embedding_client",
    "get_llm_client",
    "get_reranker_client",
    "get_document_service",
    "get_chunk_service",
    "get_rag_service",
    "get_agent_service",
    "init_vector_store",
]
