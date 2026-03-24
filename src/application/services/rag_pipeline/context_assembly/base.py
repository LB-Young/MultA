"""上下文拼接策略抽象。"""
from abc import ABC, abstractmethod


class BaseContextBuilder(ABC):
    strategy_name: str = "base"

    @abstractmethod
    def build(self, chunks) -> str:
        raise NotImplementedError
