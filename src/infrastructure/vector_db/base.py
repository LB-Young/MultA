"""向量数据库基类"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.chunk import Chunk, ChunkWithScore
from src.domain.repositories.vector_repo import VectorRepository
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class BaseVectorStore(VectorRepository):
    """向量存储基类"""
    
    def __init__(
        self,
        collection_name: str = "knowledge_base",
        vector_size: int = 1536,
        distance: str = "Cosine",
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化连接"""
        pass
    
    @abstractmethod
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """创建集合"""
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        pass
    
    @abstractmethod
    async def upsert(
        self,
        collection_name: str,
        chunks: List[Chunk],
        vectors: List[List[float]],
    ) -> List[str]:
        """插入或更新向量"""
        pass
    
    @abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: dict = None,
    ) -> List[ChunkWithScore]:
        """向量检索"""
        pass
    
    @abstractmethod
    async def delete_by_document_id(
        self,
        collection_name: str,
        document_id: str,
    ) -> int:
        """根据文档 ID 删除"""
        pass
    
    @abstractmethod
    async def get_by_id(
        self,
        collection_name: str,
        vector_id: str,
    ) -> Optional[Chunk]:
        """根据 ID 获取"""
        pass
    
    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        pass

    @abstractmethod
    async def get_by_document_id(
        self,
        collection_name: str,
        document_id: str,
    ) -> List[Chunk]:
        """根据文档 ID 获取所有切片"""
        pass

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> dict:
        """获取集合信息"""
        pass


__all__ = ["BaseVectorStore"]
