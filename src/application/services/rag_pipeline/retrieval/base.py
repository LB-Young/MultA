"""召回策略抽象。"""
from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    """召回策略基类。"""

    strategy_name: str = "base"

    @abstractmethod
    async def retrieve(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int,
        filters: dict,
    ):
        raise NotImplementedError
