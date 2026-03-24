"""查询处理组件包装器（通过工厂选择策略）。"""
from src.infrastructure.embedding import EmbeddingClient

from .query_processing_factory import QueryProcessingFactory


class QueryProcessor:
    """统一查询处理入口。"""

    def __init__(self, embedding_client: EmbeddingClient, strategy: str = "standard"):
        self.strategy = strategy
        self.factory = QueryProcessingFactory(embedding_client)
        self.impl = self.factory.create(strategy)

    async def embed(self, query_text: str) -> list[float]:
        return await self.impl.embed(query_text)
