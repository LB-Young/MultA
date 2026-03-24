"""上下文拼接工厂。"""
from .compact_context_builder import CompactContextBuilder
from .standard_context_builder import StandardContextBuilder


class ContextFactory:
    """按策略名返回上下文拼接器。"""

    def __init__(self):
        self._strategies = {
            "standard": StandardContextBuilder(),
            "compact": CompactContextBuilder(),
        }

    def create(self, strategy: str = "standard"):
        return self._strategies.get((strategy or "standard").lower(), self._strategies["standard"])
