"""召回策略工厂。"""
from src.infrastructure.vector_db import VectorStoreFactory

from .dense_retriever import DenseRetriever
from .hybrid_retriever import HybridRetriever
from .sparse_retriever import SparseRetriever


class RetrievalFactory:
    """加载并按策略名返回召回器实现。"""

    def __init__(self, collection_name: str, store=None):
        self.collection_name = collection_name
        self.store = store or VectorStoreFactory.get_store(collection_name)
        self._strategies = {
            "dense": DenseRetriever(collection_name, self.store),
            "sparse": SparseRetriever(collection_name, self.store),
            "hybrid": HybridRetriever(collection_name, self.store),
        }

    def create(self, strategy: str):
        return self._strategies.get((strategy or "dense").lower(), self._strategies["dense"])
