"""稠密召回策略。"""
from .base import BaseRetriever


class DenseRetriever(BaseRetriever):
    strategy_name = "dense"

    def __init__(self, collection_name: str, store):
        self.collection_name = collection_name
        self.store = store

    async def retrieve(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int,
        filters: dict,
    ):
        return await self.store.search(
            self.collection_name,
            query_vector,
            top_k=top_k,
            filters=filters,
        )
