"""RAG 服务测试"""
import asyncio
from datetime import datetime

from src.application.schemas.rag import RAGQueryRequest
from src.application.services.rag_service import RAGService
from src.domain.entities.chunk import Chunk, ChunkWithScore
from src.infrastructure.vector_db import VectorStoreFactory


class _FakeEmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _FakeLLMClient:
    async def chat(self, messages, system_prompt: str) -> str:
        return "测试回答"


class _FakeStore:
    async def search(self, collection_name, query_vector, top_k, filters):
        chunk = Chunk(
            document_id="doc-1",
            content="用于回答问题的测试内容",
            chunk_index=0,
            start_char=0,
            end_char=11,
        )
        return [ChunkWithScore(chunk=chunk, score=0.95, rank=1)]


class _FakeQueryProcessor:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _FakeRetriever:
    async def retrieve(self, query_text, query_vector, top_k, filters):
        chunk = Chunk(
            document_id="doc-1",
            content="用于回答问题的测试内容",
            chunk_index=0,
            start_char=0,
            end_char=11,
        )
        return [ChunkWithScore(chunk=chunk, score=0.95, rank=1)]


class _FakePipelineReranker:
    async def rerank(self, query: str, chunks, top_k: int, use_rerank: bool):
        return chunks[:top_k]


class _FakeContextBuilder:
    def build(self, chunks) -> str:
        return "[文档1]\\n用于回答问题的测试内容"


class _FakePipelineFactory:
    def __init__(self):
        self.last_collection_name = None

    def create(
        self,
        embedding_client,
        reranker_client,
        collection_name: str,
        retrieval_strategy: str = "dense",
        query_processing_strategy: str = "standard",
        reranking_strategy: str = "model",
        context_assembly_strategy: str = "standard",
    ):
        self.last_collection_name = collection_name

        class _Components:
            query_processor = _FakeQueryProcessor()
            retriever = _FakeRetriever()
            reranker = _FakePipelineReranker()
            context_builder = _FakeContextBuilder()

        return _Components()


def test_query_with_history_returns_created_at_without_member_descriptor_error(monkeypatch):
    """多轮查询应返回正常 created_at，而不是访问类级描述符报错。"""
    monkeypatch.setattr(VectorStoreFactory, "get_store", lambda collection_name: _FakeStore())
    service = RAGService(
        embedding_client=_FakeEmbeddingClient(),
        llm_client=_FakeLLMClient(),
        reranker_client=None,
    )
    request = RAGQueryRequest(text="你好", session_id="session-1", history=[])

    response = asyncio.run(service.query_with_history(request))

    assert response.answer == "测试回答"
    assert isinstance(response.created_at, datetime)


def test_query_with_history_uses_pipeline_factory(monkeypatch):
    """查询应通过 pipeline factory 组装处理链路。"""
    monkeypatch.setattr(VectorStoreFactory, "get_store", lambda collection_name: _FakeStore())
    service = RAGService(
        embedding_client=_FakeEmbeddingClient(),
        llm_client=_FakeLLMClient(),
        reranker_client=None,
    )
    fake_factory = _FakePipelineFactory()
    service.pipeline_factory = fake_factory

    request = RAGQueryRequest(text="你好", session_id="session-1", history=[])
    response = asyncio.run(service.query_with_history(request))

    assert response.answer == "测试回答"
    assert fake_factory.last_collection_name == "knowledge_base"


def test_query_with_history_passes_retrieval_strategy_to_pipeline(monkeypatch):
    """查询请求中的检索策略应透传到 pipeline 工厂。"""
    monkeypatch.setattr(VectorStoreFactory, "get_store", lambda collection_name: _FakeStore())
    service = RAGService(
        embedding_client=_FakeEmbeddingClient(),
        llm_client=_FakeLLMClient(),
        reranker_client=None,
    )

    class _CaptureFactory(_FakePipelineFactory):
        def __init__(self):
            super().__init__()
            self.last_strategy = None

        def create(
            self,
            embedding_client,
            reranker_client,
            collection_name: str,
            retrieval_strategy: str = "dense",
            query_processing_strategy: str = "standard",
            reranking_strategy: str = "model",
            context_assembly_strategy: str = "standard",
        ):
            self.last_strategy = retrieval_strategy
            return super().create(embedding_client, reranker_client, collection_name)

    capture_factory = _CaptureFactory()
    service.pipeline_factory = capture_factory

    request = RAGQueryRequest(text="你好", session_id="session-1", history=[], retrieval_strategy="hybrid")
    response = asyncio.run(service.query_with_history(request))

    assert response.answer == "测试回答"
    assert capture_factory.last_strategy == "hybrid"


def test_query_with_history_passes_all_pipeline_strategies(monkeypatch):
    """查询请求中的策略参数应透传到 pipeline 工厂。"""
    monkeypatch.setattr(VectorStoreFactory, "get_store", lambda collection_name: _FakeStore())
    service = RAGService(
        embedding_client=_FakeEmbeddingClient(),
        llm_client=_FakeLLMClient(),
        reranker_client=None,
    )

    class _CaptureFactory(_FakePipelineFactory):
        def __init__(self):
            super().__init__()
            self.last_query_processing_strategy = None
            self.last_reranking_strategy = None
            self.last_context_assembly_strategy = None

        def create(
            self,
            embedding_client,
            reranker_client,
            collection_name: str,
            retrieval_strategy: str = "dense",
            query_processing_strategy: str = "standard",
            reranking_strategy: str = "model",
            context_assembly_strategy: str = "standard",
        ):
            self.last_query_processing_strategy = query_processing_strategy
            self.last_reranking_strategy = reranking_strategy
            self.last_context_assembly_strategy = context_assembly_strategy
            return super().create(
                embedding_client,
                reranker_client,
                collection_name,
                retrieval_strategy=retrieval_strategy,
                query_processing_strategy=query_processing_strategy,
                reranking_strategy=reranking_strategy,
                context_assembly_strategy=context_assembly_strategy,
            )

    capture_factory = _CaptureFactory()
    service.pipeline_factory = capture_factory

    request = RAGQueryRequest(
        text="你好",
        session_id="session-1",
        history=[],
        query_processing_strategy="normalized",
        reranking_strategy="identity",
        context_assembly_strategy="compact",
    )
    response = asyncio.run(service.query_with_history(request))

    assert response.answer == "测试回答"
    assert capture_factory.last_query_processing_strategy == "normalized"
    assert capture_factory.last_reranking_strategy == "identity"
    assert capture_factory.last_context_assembly_strategy == "compact"
