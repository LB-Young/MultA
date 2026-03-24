"""不重排策略。"""
from .base import BaseReranker


class IdentityReranker(BaseReranker):
    strategy_name = "identity"

    async def rerank(self, query: str, chunks, top_k: int, use_rerank: bool):
        return chunks[:top_k]
