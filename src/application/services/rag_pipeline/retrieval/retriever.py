"""召回组件包装器（通过工厂选择策略）。"""
from .retrieval_factory import RetrievalFactory


class Retriever:
    """统一召回入口，内部委托到具体策略。"""

    def __init__(self, collection_name: str, strategy: str = "dense"):
        self.collection_name = collection_name
        self.strategy = strategy
        self.factory = RetrievalFactory(collection_name)
        self.impl = self.factory.create(strategy)

    async def retrieve(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int,
        filters: dict,
    ):
        return await self.impl.retrieve(
            query_text=query_text,
            query_vector=query_vector,
            top_k=top_k,
            filters=filters,
        )
