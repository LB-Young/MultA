"""排序组件包装器（通过工厂选择策略）。"""
from src.infrastructure.reranker import RerankerClient

from .reranking_factory import RerankingFactory


class PipelineReranker:
    """统一排序入口。"""

    def __init__(self, reranker_client: RerankerClient | None, strategy: str = "model"):
        self.strategy = strategy
        self.factory = RerankingFactory(reranker_client)
        self.impl = self.factory.create(strategy)

    async def rerank(self, query: str, chunks, top_k: int, use_rerank: bool):
        return await self.impl.rerank(
            query=query,
            chunks=chunks,
            top_k=top_k,
            use_rerank=use_rerank,
        )
