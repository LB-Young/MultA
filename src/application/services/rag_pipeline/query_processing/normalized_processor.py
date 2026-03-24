"""归一化查询处理策略。"""
from src.infrastructure.embedding import EmbeddingClient

from .base import BaseQueryProcessor


class NormalizedQueryProcessor(BaseQueryProcessor):
    strategy_name = "normalized"

    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client

    async def embed(self, query_text: str) -> list[float]:
        normalized = " ".join((query_text or "").strip().split())
        return await self.embedding_client.embed(normalized)
