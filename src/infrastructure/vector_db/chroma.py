"""Chroma 向量数据库"""
from typing import List, Optional

from src.domain.entities.chunk import Chunk, ChunkWithScore
from src.infrastructure.vector_db.base import BaseVectorStore
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class ChromaVectorStore(BaseVectorStore):
    """Chroma 向量数据库实现"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "knowledge_base",
        vector_size: int = 1536,
        distance: str = "Cosine",
    ):
        super().__init__(collection_name, vector_size, distance)
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
    
    def _get_client(self):
        """获取 Chroma 客户端"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )
            except ImportError:
                raise ImportError("请安装 chromadb: pip install chromadb")
        return self._client
    
    async def initialize(self) -> None:
        """初始化连接"""
        try:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance.lower()},
            )
            self._initialized = True
            logger.info(f"Chroma 连接成功: {self.persist_directory}")
        except Exception as e:
            from src.infrastructure.exceptions import VectorStoreConnectionError
            raise VectorStoreConnectionError(f"Chroma 连接失败: {e}")
    
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """创建集合"""
        client = self._get_client()
        
        try:
            client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": distance.lower()},
            )
            logger.info(f"Chroma 集合已创建: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"创建 Chroma 集合失败: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        client = self._get_client()
        
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Chroma 集合已删除: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"删除 Chroma 集合失败: {e}")
            return False
    
    async def upsert(
        self,
        collection_name: str,
        chunks: List[Chunk],
        vectors: List[List[float]],
    ) -> List[str]:
        """插入或更新向量"""
        client = self._get_client()
        
        try:
            collection = client.get_collection(collection_name)
            
            ids = [chunk.id for chunk in chunks]
            embeddings = vectors
            metadatas = [
                {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "length": chunk.length,
                    **chunk.metadata,
                }
                for chunk in chunks
            ]
            documents = [chunk.content for chunk in chunks]
            
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
            )
            
            logger.debug(f"Chroma 插入 {len(chunks)} 条向量")
            return ids
            
        except Exception as e:
            logger.error(f"Chroma 插入向量失败: {e}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: dict = None,
    ) -> List[ChunkWithScore]:
        """向量检索"""
        client = self._get_client()
        
        try:
            collection = client.get_collection(collection_name)
            
            where = None
            if filters:
                where = filters
            
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where,
                include=["metadatas", "documents", "distances"],
            )
            
            chunks_with_scores = []
            
            if results["ids"] and results["ids"][0]:
                for i, (chunk_id, document, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )):
                    chunk = Chunk(
                        id=chunk_id,
                        document_id=metadata.get("document_id", ""),
                        content=document,
                        chunk_index=metadata.get("chunk_index", 0),
                        start_char=metadata.get("start_char", 0),
                        end_char=metadata.get("end_char", 0),
                        length=metadata.get("length", 0),
                        metadata=metadata,
                        vector_id=chunk_id,
                    )
                    
                    # Chroma 返回的是距离，转换为相似度分数
                    score = 1.0 / (1.0 + distance)
                    
                    chunks_with_scores.append(
                        ChunkWithScore(chunk=chunk, score=score, rank=i + 1)
                    )
            
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"Chroma 检索失败: {e}")
            raise
    
    async def delete_by_document_id(
        self,
        collection_name: str,
        document_id: str,
    ) -> int:
        """根据文档 ID 删除"""
        client = self._get_client()
        
        try:
            collection = client.get_collection(collection_name)
            
            # 获取所有文档的 ID
            all_data = collection.get(include=["metadatas"])
            
            # 找到匹配 document_id 的记录
            ids_to_delete = [
                id_
                for id_, metadata in zip(all_data["ids"], all_data["metadatas"])
                if metadata.get("document_id") == document_id
            ]
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.info(f"Chroma 删除文档 {document_id} 的 {len(ids_to_delete)} 条向量")
            
            return len(ids_to_delete)
            
        except Exception as e:
            logger.error(f"Chroma 删除向量失败: {e}")
            return 0
    
    async def get_by_id(
        self,
        collection_name: str,
        vector_id: str,
    ) -> Optional[Chunk]:
        """根据 ID 获取"""
        client = self._get_client()
        
        try:
            collection = client.get_collection(collection_name)
            
            results = collection.get(
                ids=[vector_id],
                include=["metadatas", "documents"],
            )
            
            if not results["ids"]:
                return None
            
            return Chunk(
                id=results["ids"][0],
                document_id=results["metadatas"][0].get("document_id", ""),
                content=results["documents"][0],
                chunk_index=results["metadatas"][0].get("chunk_index", 0),
                start_char=results["metadatas"][0].get("start_char", 0),
                end_char=results["metadatas"][0].get("end_char", 0),
                length=results["metadatas"][0].get("length", 0),
                metadata=results["metadatas"][0],
                vector_id=results["ids"][0],
            )
            
        except Exception as e:
            logger.error(f"Chroma 获取向量失败: {e}")
            return None
    
    async def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        client = self._get_client()
        
        try:
            client.get_collection(collection_name)
            return True
        except Exception:
            return False
    
    async def get_by_document_id(
        self,
        collection_name: str,
        document_id: str,
    ) -> List[Chunk]:
        """根据文档 ID 获取所有切片"""
        client = self._get_client()

        try:
            collection = client.get_collection(collection_name)

            results = collection.get(
                where={"document_id": document_id},
                include=["metadatas", "documents"],
            )

            if not results["ids"]:
                return []

            chunks = []
            for chunk_id, document, metadata in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
            ):
                chunks.append(Chunk(
                    id=chunk_id,
                    document_id=metadata.get("document_id", ""),
                    content=document,
                    chunk_index=metadata.get("chunk_index", 0),
                    start_char=metadata.get("start_char", 0),
                    end_char=metadata.get("end_char", 0),
                    length=metadata.get("length", 0),
                    metadata=metadata,
                    vector_id=chunk_id,
                ))

            # 按 chunk_index 排序
            chunks.sort(key=lambda c: c.chunk_index)
            return chunks

        except Exception as e:
            logger.error(f"Chroma 按文档 ID 获取切片失败: {e}")
            return []

    async def get_collection_info(self, collection_name: str) -> dict:
        """获取集合信息"""
        client = self._get_client()
        
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "vectors_count": count,
                "points_count": count,
                "status": "ready",
            }
        except Exception as e:
            from src.infrastructure.exceptions import CollectionNotFoundError
            raise CollectionNotFoundError(collection_name)


__all__ = ["ChromaVectorStore"]
