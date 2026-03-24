"""排序策略抽象。"""
from abc import ABC, abstractmethod


class BaseReranker(ABC):
    strategy_name: str = "base"

    @abstractmethod
    async def rerank(self, query: str, chunks, top_k: int, use_rerank: bool):
        raise NotImplementedError
