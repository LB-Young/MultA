"""查询处理策略抽象。"""
from abc import ABC, abstractmethod


class BaseQueryProcessor(ABC):
    strategy_name: str = "base"

    @abstractmethod
    async def embed(self, query_text: str) -> list[float]:
        raise NotImplementedError
