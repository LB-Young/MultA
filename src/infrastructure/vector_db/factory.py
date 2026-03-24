"""向量数据库工厂"""
from typing import Optional

from src.domain.repositories.vector_repo import VectorRepository
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class VectorStoreFactory:
    """向量数据库工厂"""
    
    _stores: dict = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, config: dict) -> None:
        """初始化向量数据库
        
        Args:
            config: 配置字典，包含 type, host, port, collection_name 等
        """
        if cls._initialized:
            return
        
        db_type = config.get("type", "qdrant")
        collection_name = config.get("collection_name", "knowledge_base")
        vector_size = config.get("vector_size", 1536)
        distance = config.get("distance", "Cosine")
        
        if db_type == "qdrant":
            store = cls._create_qdrant(
                host=config.get("host", "localhost"),
                port=config.get("port", 6333),
                collection_name=collection_name,
                vector_size=vector_size,
                distance=distance,
                api_key=config.get("api_key"),
            )
        elif db_type == "chroma":
            store = cls._create_chroma(
                persist_directory=config.get("persist_directory", "./chroma_db"),
                collection_name=collection_name,
                vector_size=vector_size,
                distance=distance,
            )
        else:
            raise ValueError(f"不支持的向量数据库类型: {db_type}")
        
        cls._stores[collection_name] = store
        cls._initialized = True
        
        logger.info(f"向量数据库已初始化: {db_type}")
    
    @classmethod
    def _create_qdrant(cls, **kwargs) -> "QdrantVectorStore":
        from .qdrant import QdrantVectorStore
        return QdrantVectorStore(**kwargs)
    
    @classmethod
    def _create_chroma(cls, **kwargs) -> "ChromaVectorStore":
        from .chroma import ChromaVectorStore
        return ChromaVectorStore(**kwargs)
    
    @classmethod
    def get_store(cls, collection_name: str = None) -> VectorRepository:
        """获取向量存储实例
        
        Args:
            collection_name: 集合名称
            
        Returns:
            向量存储实例
        """
        if not cls._initialized:
            raise RuntimeError("向量数据库未初始化，请先调用 initialize()")
        
        if collection_name is None:
            collection_name = list(cls._stores.keys())[0] if cls._stores else "knowledge_base"
        
        if collection_name not in cls._stores:
            raise ValueError(f"向量存储不存在: {collection_name}")
        
        return cls._stores[collection_name]
    
    @classmethod
    async def create_collection(
        cls,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """创建集合"""
        store = cls.get_store(collection_name)
        return await store.create_collection(collection_name, vector_size, distance)
    
    @classmethod
    async def ensure_collection(cls, collection_name: str, vector_size: int) -> bool:
        """确保集合存在"""
        store = cls.get_store(collection_name)
        
        if not await store.collection_exists(collection_name):
            await store.create_collection(collection_name, vector_size)
            return True
        return False


__all__ = ["VectorStoreFactory"]
