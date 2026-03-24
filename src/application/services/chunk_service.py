"""切片服务"""
from typing import List, Optional, Tuple

from src.domain.entities.chunk import Chunk, ChunkResponse
from src.domain.entities.document import Document
from src.infrastructure.extractors import ExtractorFactory
from src.infrastructure.chunkers import ChunkerFactory
from src.infrastructure.embedding import EmbeddingClient
from src.infrastructure.vector_db import VectorStoreFactory
from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import (
    EmptyContentError,
    ExtractionFailedError,
    ChunkingFailedError,
)
from .document_service import DocumentService

logger = get_logger(__name__)


class ChunkService:
    """切片服务"""
    
    def __init__(
        self,
        document_service: DocumentService,
        embedding_client: EmbeddingClient,
    ):
        self.document_service = document_service
        self.embedding_client = embedding_client
    
    async def process_document(
        self,
        document_id: str,
        chunk_size: int = 500,
        overlap: int = 50,
        strategy: str = "fixed_chars",
    ) -> Tuple[List[Chunk], List[List[float]]]:
        """处理文档，生成切片和向量
        
        Args:
            document_id: 文档 ID
            chunk_size: 块大小
            overlap: 重叠大小
            strategy: 切片策略
            
        Returns:
            (切片列表, 向量列表)
        """
        # 获取文档
        document = await self.document_service.get_document(document_id)
        
        # 更新状态为处理中
        await self.document_service.update_status(document_id, document.status.PROCESSING)
        
        try:
            # 1. 提取文本
            extractor = ExtractorFactory.get_extractor(document.file_type)
            text = extractor.extract(document.file_path)
            
            if not text or not text.strip():
                raise EmptyContentError(document_id)
            
            logger.debug(f"文档提取完成: {document_id}, 文本长度: {len(text)}")
            
            # 2. 切片
            chunker = ChunkerFactory.get_chunker(
                strategy=strategy,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            chunks = chunker.chunk(text, document_id=document_id)
            
            if not chunks:
                raise ChunkingFailedError("未能生成任何切片")
            
            logger.debug(f"文档切片完成: {document_id}, 生成 {len(chunks)} 个切片")
            
            # 3. 向量化
            texts = [chunk.content for chunk in chunks]
            vectors = await self.embedding_client.embed_batch(texts)
            
            logger.debug(f"文档向量化完成: {document_id}, 生成 {len(vectors)} 个向量")
            
            # 4. 更新文档状态
            await self.document_service.update_status(document_id, document.status.PROCESSED)
            document.text_length = len(text)
            document.chunk_count = len(chunks)
            
            return chunks, vectors
            
        except Exception as e:
            logger.error(f"文档处理失败: {document_id} - {e}")
            await self.document_service.update_status(
                document_id, 
                document.status.FAILED,
                error_message=str(e),
            )
            raise
    
    async def store_chunks(
        self,
        document_id: str,
        chunks: List[Chunk],
        vectors: List[List[float]],
        collection_name: str = "knowledge_base",
    ) -> List[str]:
        """存储切片到向量数据库
        
        Args:
            document_id: 文档 ID
            chunks: 切片列表
            vectors: 向量列表
            collection_name: 集合名称
            
        Returns:
            向量 ID 列表
        """
        store = VectorStoreFactory.get_store(collection_name)
        
        # 确保集合存在
        await VectorStoreFactory.ensure_collection(
            collection_name,
            len(vectors[0]) if vectors else 1536,
        )
        
        # 存储
        vector_ids = await store.upsert(collection_name, chunks, vectors)
        
        # 更新切片的向量 ID
        for chunk, vector_id in zip(chunks, vector_ids):
            chunk.set_vector_id(vector_id)
        
        logger.info(f"切片已存储: {document_id}, 数量: {len(vector_ids)}")
        
        return vector_ids
    
    async def get_chunks_by_document(
        self,
        document_id: str,
        collection_name: str = "knowledge_base",
    ) -> List[Chunk]:
        """获取文档的所有切片"""
        store = VectorStoreFactory.get_store(collection_name)
        return await store.get_by_document_id(collection_name, document_id)
    
    def to_response(self, chunk: Chunk, score: float = None) -> ChunkResponse:
        """转换为响应模型"""
        return ChunkResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            start_char=chunk.start_char,
            end_char=chunk.end_char,
            length=chunk.length,
            score=score,
        )


__all__ = ["ChunkService"]
