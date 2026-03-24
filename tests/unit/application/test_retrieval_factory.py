"""检索工厂策略选择测试"""
import asyncio

from src.application.services.rag_pipeline.retrieval.retrieval_factory import (
    RetrievalFactory,
)


class _FakeStore:
    async def search(self, collection_name, query_vector, top_k, filters):
        return []


def test_retrieval_factory_builds_dense_by_default():
    factory = RetrievalFactory(collection_name="kb", store=_FakeStore())
    retriever = factory.create("dense")
    assert retriever.strategy_name == "dense"


def test_retrieval_factory_builds_sparse_and_hybrid():
    factory = RetrievalFactory(collection_name="kb", store=_FakeStore())
    assert factory.create("sparse").strategy_name == "sparse"
    assert factory.create("hybrid").strategy_name == "hybrid"


def test_retrieval_factory_fallbacks_to_dense_on_unknown_strategy():
    factory = RetrievalFactory(collection_name="kb", store=_FakeStore())
    retriever = factory.create("unknown_strategy")
    assert retriever.strategy_name == "dense"


def test_sparse_and_hybrid_retrievers_keep_async_contract():
    factory = RetrievalFactory(collection_name="kb", store=_FakeStore())
    sparse = factory.create("sparse")
    hybrid = factory.create("hybrid")

    sparse_result = asyncio.run(
        sparse.retrieve(query_text="hello", query_vector=[0.1], top_k=3, filters={})
    )
    hybrid_result = asyncio.run(
        hybrid.retrieve(query_text="hello", query_vector=[0.1], top_k=3, filters={})
    )
    assert sparse_result == []
    assert hybrid_result == []
