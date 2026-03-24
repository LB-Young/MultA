"""标准查询处理策略。"""
from src.infrastructure.embedding import EmbeddingClient

from .base import BaseQueryProcessor


class StandardQueryProcessor(BaseQueryProcessor):
    strategy_name = "standard"

    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client

    async def embed(self, query_text: str) -> list[float]:
        return await self.embedding_client.embed(query_text)
