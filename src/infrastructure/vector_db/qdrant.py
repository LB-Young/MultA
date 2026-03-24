"""Qdrant 向量数据库"""
from typing import List, Optional

from src.domain.entities.chunk import Chunk, ChunkWithScore
from src.infrastructure.vector_db.base import BaseVectorStore
from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import VectorStoreConnectionError, CollectionNotFoundError

logger = get_logger(__name__)


class QdrantVectorStore(BaseVectorStore):
    """Qdrant 向量数据库实现"""
    
    DISTANCE_MAP = {
        "Cosine": "Cosine",
        "Euclid": "Euclid",
        "Dot": "Dot",
    }
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "knowledge_base",
        vector_size: int = 1536,
        distance: str = "Cosine",
        api_key: str = None,
    ):
        super().__init__(collection_name, vector_size, distance)
        self.host = host
        self.port = port
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """获取 Qdrant 客户端"""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                self._client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key,
                )
            except ImportError:
                raise ImportError("请安装 qdrant-client: pip install qdrant-client")
        return self._client
    
    async def initialize(self) -> None:
        """初始化连接"""
        try:
            client = self._get_client()
            # 测试连接
            client.get_collections()
            self._initialized = True
            logger.info(f"Qdrant 连接成功: {self.host}:{self.port}")
        except Exception as e:
            raise VectorStoreConnectionError(f"Qdrant 连接失败: {e}")
    
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """创建集合"""
        client = self._get_client()
        
        try:
            from qdrant_client.http.models import Distance, VectorParams
            from qdrant_client.models import Distance as QdrantDistance
            
            distance_map = {
                "Cosine": QdrantDistance.COSINE,
                "Euclid": QdrantDistance.EUCLID,
                "Dot": QdrantDistance.DOT,
            }
            
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, QdrantDistance.COSINE),
                ),
            )
            
            logger.info(f"Qdrant 集合已创建: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建 Qdrant 集合失败: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        client = self._get_client()
        
        try:
            client.delete_collection(collection_name=collection_name)
            logger.info(f"Qdrant 集合已删除: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"删除 Qdrant 集合失败: {e}")
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
            from qdrant_client.models import PointStruct
            
            points = [
                PointStruct(
                    id=chunk.id,
                    vector=vector,
                    payload={
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "length": chunk.length,
                        "metadata": chunk.metadata,
                    },
                )
                for chunk, vector in zip(chunks, vectors)
            ]
            
            client.upsert(
                collection_name=collection_name,
                points=points,
            )
            
            logger.debug(f"Qdrant 插入 {len(points)} 条向量")
            return [p.id for p in points]
            
        except Exception as e:
            logger.error(f"Qdrant 插入向量失败: {e}")
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
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            search_params = {"limit": top_k}
            
            # 构建过滤条件
            query_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                if must_conditions:
                    query_filter = Filter(must=must_conditions)
            
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                **search_params,
            )
            
            chunks_with_scores = []
            for i, result in enumerate(results):
                chunk = Chunk(
                    id=result.id,
                    document_id=result.payload.get("document_id", ""),
                    content=result.payload.get("content", ""),
                    chunk_index=result.payload.get("chunk_index", 0),
                    start_char=result.payload.get("start_char", 0),
                    end_char=result.payload.get("end_char", 0),
                    length=result.payload.get("length", 0),
                    metadata=result.payload.get("metadata", {}),
                    vector_id=result.id,
                )
                chunks_with_scores.append(
                    ChunkWithScore(chunk=chunk, score=result.score, rank=i + 1)
                )
            
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"Qdrant 检索失败: {e}")
            raise
    
    async def delete_by_document_id(
        self,
        collection_name: str,
        document_id: str,
    ) -> int:
        """根据文档 ID 删除"""
        client = self._get_client()
        
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                ),
            )
            
            logger.info(f"Qdrant 删除文档 {document_id} 的向量")
            return 1  # 实际删除数量不可知
            
        except Exception as e:
            logger.error(f"Qdrant 删除向量失败: {e}")
            return 0
    
    async def get_by_id(
        self,
        collection_name: str,
        vector_id: str,
    ) -> Optional[Chunk]:
        """根据 ID 获取"""
        client = self._get_client()
        
        try:
            results = client.retrieve(
                collection_name=collection_name,
                ids=[vector_id],
            )
            
            if not results:
                return None
            
            result = results[0]
            return Chunk(
                id=result.id,
                document_id=result.payload.get("document_id", ""),
                content=result.payload.get("content", ""),
                chunk_index=result.payload.get("chunk_index", 0),
                start_char=result.payload.get("start_char", 0),
                end_char=result.payload.get("end_char", 0),
                length=result.payload.get("length", 0),
                metadata=result.payload.get("metadata", {}),
                vector_id=result.id,
            )
            
        except Exception as e:
            logger.error(f"Qdrant 获取向量失败: {e}")
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
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            results = client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                ),
                with_payload=True,
                limit=10000,
            )

            chunks = []
            for result in results[0]:
                chunks.append(Chunk(
                    id=str(result.id),
                    document_id=result.payload.get("document_id", ""),
                    content=result.payload.get("content", ""),
                    chunk_index=result.payload.get("chunk_index", 0),
                    start_char=result.payload.get("start_char", 0),
                    end_char=result.payload.get("end_char", 0),
                    length=result.payload.get("length", 0),
                    metadata=result.payload.get("metadata", {}),
                    vector_id=str(result.id),
                ))

            chunks.sort(key=lambda c: c.chunk_index)
            return chunks

        except Exception as e:
            logger.error(f"Qdrant 按文档 ID 获取切片失败: {e}")
            return []

    async def get_collection_info(self, collection_name: str) -> dict:
        """获取集合信息"""
        client = self._get_client()
        
        try:
            info = client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status),
            }
        except Exception as e:
            raise CollectionNotFoundError(collection_name)


__all__ = ["QdrantVectorStore"]
