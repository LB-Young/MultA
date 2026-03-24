"""查询处理/排序/上下文工厂测试。"""
import asyncio

from src.application.services.rag_pipeline.context_assembly.context_factory import ContextFactory
from src.application.services.rag_pipeline.query_processing.query_processing_factory import (
    QueryProcessingFactory,
)
from src.application.services.rag_pipeline.reranking.reranking_factory import RerankingFactory
from src.domain.entities.chunk import Chunk, ChunkWithScore


class _FakeEmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        return [float(len(text))]


class _FakeRerankerClient:
    async def rerank(self, query, documents, top_k):
        return [(0, 0.9)]


def test_query_processing_factory_supports_standard_and_normalized():
    factory = QueryProcessingFactory(_FakeEmbeddingClient())
    assert factory.create("standard").strategy_name == "standard"
    assert factory.create("normalized").strategy_name == "normalized"
    assert factory.create("unknown").strategy_name == "standard"

    normalized_processor = factory.create("normalized")
    result = asyncio.run(normalized_processor.embed("  a   b  "))
    assert result == [3.0]


def test_reranking_factory_supports_model_and_identity():
    factory = RerankingFactory(_FakeRerankerClient())
    assert factory.create("model").strategy_name == "model"
    assert factory.create("identity").strategy_name == "identity"
    assert factory.create("unknown").strategy_name == "model"

    chunk = Chunk(
        document_id="doc-1",
        content="测试内容",
        chunk_index=0,
        start_char=0,
        end_char=4,
    )
    chunks = [ChunkWithScore(chunk=chunk, score=0.5, rank=1)]
    identity = factory.create("identity")
    reranked = asyncio.run(identity.rerank("q", chunks, top_k=1, use_rerank=True))
    assert len(reranked) == 1


def test_context_factory_supports_standard_and_compact():
    factory = ContextFactory()
    assert factory.create("standard").strategy_name == "standard"
    assert factory.create("compact").strategy_name == "compact"
    assert factory.create("unknown").strategy_name == "standard"

    chunk = Chunk(
        document_id="doc-1",
        content="x" * 400,
        chunk_index=0,
        start_char=0,
        end_char=400,
    )
    chunks = [ChunkWithScore(chunk=chunk, score=0.8, rank=1)]
    compact = factory.create("compact")
    context = compact.build(chunks)
    assert len(context) < 360
