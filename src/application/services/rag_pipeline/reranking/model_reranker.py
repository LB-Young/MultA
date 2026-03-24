"""模型重排策略。"""
from src.domain.entities.chunk import ChunkWithScore
from src.infrastructure.reranker import RerankerClient

from .base import BaseReranker


class ModelReranker(BaseReranker):
    strategy_name = "model"

    def __init__(self, reranker_client: RerankerClient | None):
        self.reranker_client = reranker_client

    async def rerank(
        self,
        query: str,
        chunks: list[ChunkWithScore],
        top_k: int,
        use_rerank: bool,
    ) -> list[ChunkWithScore]:
        if not use_rerank or not self.reranker_client:
            return chunks[:top_k]

        documents = [c.chunk.content for c in chunks]
        results = await self.reranker_client.rerank(query, documents, top_k)
        reranked: list[ChunkWithScore] = []
        for idx, score in results[:top_k]:
            chunk = chunks[idx].chunk
            reranked.append(
                ChunkWithScore(
                    chunk=chunk,
                    score=score,
                    rank=len(reranked) + 1,
                )
            )
        return reranked
