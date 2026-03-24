"""查询处理工厂。"""
from src.infrastructure.embedding import EmbeddingClient

from .normalized_processor import NormalizedQueryProcessor
from .standard_processor import StandardQueryProcessor


class QueryProcessingFactory:
    """按策略名提供查询处理器。"""

    def __init__(self, embedding_client: EmbeddingClient):
        self._strategies = {
            "standard": StandardQueryProcessor(embedding_client),
            "normalized": NormalizedQueryProcessor(embedding_client),
        }

    def create(self, strategy: str = "standard"):
        return self._strategies.get((strategy or "standard").lower(), self._strategies["standard"])
