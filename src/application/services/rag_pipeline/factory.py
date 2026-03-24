"""RAG Pipeline 工厂。"""
from dataclasses import dataclass

from src.infrastructure.embedding import EmbeddingClient
from src.infrastructure.reranker import RerankerClient

from .context_assembly.context_builder import ContextBuilder
from .query_processing.processor import QueryProcessor
from .reranking.reranker import PipelineReranker
from .retrieval.retriever import Retriever


@dataclass
class RAGPipelineComponents:
    """RAG 查询链路组件集合。"""

    query_processor: QueryProcessor
    retriever: Retriever
    reranker: PipelineReranker
    context_builder: ContextBuilder


class RAGPipelineFactory:
    """根据运行参数创建 RAG pipeline 组件。"""

    def create(
        self,
        embedding_client: EmbeddingClient,
        reranker_client: RerankerClient | None,
        collection_name: str,
        retrieval_strategy: str = "dense",
        query_processing_strategy: str = "standard",
        reranking_strategy: str = "model",
        context_assembly_strategy: str = "standard",
    ) -> RAGPipelineComponents:
        return RAGPipelineComponents(
            query_processor=QueryProcessor(embedding_client, strategy=query_processing_strategy),
            retriever=Retriever(collection_name, strategy=retrieval_strategy),
            reranker=PipelineReranker(reranker_client, strategy=reranking_strategy),
            context_builder=ContextBuilder(strategy=context_assembly_strategy),
        )
