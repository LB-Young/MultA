"""向量仓储接口"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..entities.chunk import Chunk, ChunkWithScore


class VectorRepository(ABC):
    """向量仓储接口
    
    定义向量存储和检索操作
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化向量存储"""
        ...
    
    @abstractmethod
    async def create_collection(
        self, 
        collection_name: str, 
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """创建向量集合
        
        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            distance: 距离度量方式
            
        Returns:
            是否创建成功
        """
        ...
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """删除向量集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否删除成功
        """
        ...
    
    @abstractmethod
    async def upsert(
        self, 
        collection_name: str, 
        chunks: List[Chunk],
        vectors: List[List[float]],
    ) -> List[str]:
        """批量插入或更新向量
        
        Args:
            collection_name: 集合名称
            chunks: 切片列表
            vectors: 向量列表
            
        Returns:
            插入的 ID 列表
        """
        ...
    
    @abstractmethod
    async def search(
        self, 
        collection_name: str, 
        query_vector: List[float],
        top_k: int = 5,
        filters: dict = None,
    ) -> List[ChunkWithScore]:
        """向量检索
        
        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            top_k: 返回数量
            filters: 过滤条件
            
        Returns:
            相关切片列表（带分数）
        """
        ...
    
    @abstractmethod
    async def delete_by_document_id(
        self, 
        collection_name: str, 
        document_id: str,
    ) -> int:
        """根据文档 ID 删除向量
        
        Args:
            collection_name: 集合名称
            document_id: 文档 ID
            
        Returns:
            删除数量
        """
        ...
    
    @abstractmethod
    async def get_by_id(
        self, 
        collection_name: str, 
        vector_id: str,
    ) -> Optional[Chunk]:
        """根据 ID 获取切片
        
        Args:
            collection_name: 集合名称
            vector_id: 向量 ID
            
        Returns:
            切片实体
        """
        ...
    
    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否存在
        """
        ...
    
    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> dict:
        """获取集合信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            集合信息
        """
        ...


__all__ = ["VectorRepository"]
