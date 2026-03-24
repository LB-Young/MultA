"""文档服务"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.domain.entities.document import (
    Document, 
    DocumentStatus, 
    DocumentType,
    DocumentResponse,
)
from src.domain.repositories.document_repo import DocumentRepository
from src.infrastructure.storage.file_storage import FileStorage
from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import DocumentNotFoundError, ExtractionFailedError

logger = get_logger(__name__)


class DocumentService:
    """文档服务"""
    
    def __init__(
        self,
        storage: FileStorage,
        repository: DocumentRepository,
    ):
        self.storage = storage
        self.repository = repository
    
    async def upload_document(
        self,
        file_content: bytes,
        filename: str,
    ) -> Document:
        """上传文档
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            文档实体
        """
        # 保存文件
        document = await self.storage.save_file(file_content, filename)
        
        # 保存到仓储
        await self.repository.save(document)
        
        logger.info(f"文档上传成功: {filename}, ID: {document.id}")
        
        return document
    
    async def get_document(self, document_id: str) -> Document:
        """获取文档
        
        Args:
            document_id: 文档 ID
            
        Returns:
            文档实体
        """
        document = await self.repository.get_by_id(document_id)
        
        if document is None:
            raise DocumentNotFoundError(document_id)
        
        return document
    
    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
    ) -> List[Document]:
        """列出文档
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            status: 状态过滤
            
        Returns:
            文档列表
        """
        return await self.repository.list(skip, limit, status)
    
    async def delete_document(self, document_id: str) -> bool:
        """删除文档
        
        Args:
            document_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        document = await self.get_document(document_id)
        
        # 删除文件
        await self.storage.delete_file(document.file_path)
        
        # 从仓储删除
        await self.repository.delete(document_id)
        
        logger.info(f"文档已删除: {document_id}")
        
        return True
    
    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        error_message: str = None,
    ) -> Document:
        """更新文档状态

        Args:
            document_id: 文档 ID
            status: 新状态
            error_message: 错误信息

        Returns:
            更新后的文档
        """
        document = await self.get_document(document_id)

        document.status = status
        document.updated_at = datetime.now()

        if error_message:
            document.error_message = error_message

        return await self.repository.update(document)

    async def update_metadata(
        self,
        document_id: str,
        text_length: int,
        chunk_count: int,
    ) -> Document:
        """更新文档元数据（处理完成后调用）"""
        document = await self.get_document(document_id)
        document.text_length = text_length
        document.chunk_count = chunk_count
        document.updated_at = datetime.now()
        return await self.repository.update(document)
    
    def to_response(self, document: Document) -> DocumentResponse:
        """转换为响应模型"""
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            file_type=document.file_type.value,
            status=document.status.value,
            text_length=document.text_length,
            chunk_count=document.chunk_count,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


__all__ = ["DocumentService"]
