"""排序工厂。"""
from src.infrastructure.reranker import RerankerClient

from .identity_reranker import IdentityReranker
from .model_reranker import ModelReranker


class RerankingFactory:
    """按策略名返回排序器。"""

    def __init__(self, reranker_client: RerankerClient | None):
        self._strategies = {
            "identity": IdentityReranker(),
            "model": ModelReranker(reranker_client),
        }

    def create(self, strategy: str = "model"):
        return self._strategies.get((strategy or "model").lower(), self._strategies["model"])
