"""上下文拼接组件包装器（通过工厂选择策略）。"""
from .context_factory import ContextFactory


class ContextBuilder:
    """统一上下文拼接入口。"""

    def __init__(self, strategy: str = "standard"):
        self.strategy = strategy
        self.factory = ContextFactory()
        self.impl = self.factory.create(strategy)

    def build(self, chunks) -> str:
        return self.impl.build(chunks)
