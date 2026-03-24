"""文档仓储接口"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.document import Document


class DocumentRepository(ABC):
    """文档仓储接口
    
    定义文档的持久化操作
    """
    
    @abstractmethod
    async def save(self, document: Document) -> Document:
        """保存文档
        
        Args:
            document: 文档实体
            
        Returns:
            保存后的文档
        """
        ...
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """根据 ID 获取文档
        
        Args:
            document_id: 文档 ID
            
        Returns:
            文档实体，不存在返回 None
        """
        ...
    
    @abstractmethod
    async def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: str = None,
    ) -> List[Document]:
        """列出文档
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            status: 按状态过滤
            
        Returns:
            文档列表
        """
        ...
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """删除文档
        
        Args:
            document_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        ...
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """更新文档
        
        Args:
            document: 文档实体
            
        Returns:
            更新后的文档
        """
        ...
    
    @abstractmethod
    async def count(self, status: str = None) -> int:
        """统计文档数量
        
        Args:
            status: 按状态过滤
            
        Returns:
            文档数量
        """
        ...


__all__ = ["DocumentRepository"]
