"""RAG 服务"""
import time
from typing import List, Optional, Dict, Any
from uuid import uuid4

from src.domain.entities.chunk import ChunkWithScore
from src.domain.entities.query import (
    Query,
    QueryResult,
    QueryRequest,
    QueryResponse,
    ConversationSession,
    ConversationMessage,
)
from src.infrastructure.embedding import EmbeddingClient
from src.infrastructure.llm import LLMClient
from src.infrastructure.reranker import RerankerClient
from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import NoRelevantChunksError, LLMError
from src.application.schemas.rag import RAGQueryRequest, HistoryMessage
from src.application.services.rag_pipeline import RAGPipelineFactory

logger = get_logger(__name__)


class RAGService:
    """RAG 服务"""

    DEFAULT_SYSTEM_PROMPT = """你是一个知识库问答助手，专注于回答用户关于知识库中的问题。

请遵循以下规则：
1. 只回答与知识库内容相关的问题
2. 如果知识库中没有相关信息，请如实告知用户
3. 回答要准确、简洁、有条理
4. 如果需要引用知识库内容，请注明来源
"""

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        llm_client: LLMClient,
        reranker_client: RerankerClient = None,
    ):
        self.embedding_client = embedding_client
        self.llm_client = llm_client
        self.reranker_client = reranker_client
        self.pipeline_factory = RAGPipelineFactory()

    async def query(
        self,
        request: QueryRequest,
        collection_name: str = "knowledge_base",
    ) -> QueryResponse:
        """处理查询请求"""
        start_time = time.time()
        pipeline = self.pipeline_factory.create(
            embedding_client=self.embedding_client,
            reranker_client=self.reranker_client,
            collection_name=collection_name,
            retrieval_strategy=getattr(request, "retrieval_strategy", "dense"),
            query_processing_strategy=getattr(request, "query_processing_strategy", "standard"),
            reranking_strategy=getattr(request, "reranking_strategy", "model"),
            context_assembly_strategy=getattr(request, "context_assembly_strategy", "standard"),
        )

        # 1. 向量化查询
        query_vector = await pipeline.query_processor.embed(request.text)

        # 2. 检索相关切片
        chunks_with_scores = await pipeline.retriever.retrieve(
            query_text=request.text,
            query_vector=query_vector,
            top_k=request.top_k,
            filters=request.filters,
        )

        if not chunks_with_scores:
            raise NoRelevantChunksError(request.text)

        # 3. Rerank（如果启用）
        chunks_with_scores = await pipeline.reranker.rerank(
            query=request.text,
            chunks=chunks_with_scores,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
        )

        # 4. 构建上下文
        context = pipeline.context_builder.build(chunks_with_scores)

        # 5. 生成回答
        answer = await self._generate_answer(
            query=request.text,
            context=context,
            chunks=chunks_with_scores,
        )

        generation_time = time.time() - start_time

        query_result = QueryResult(
            id=str(uuid4()),
            query_id="",
            answer=answer,
            sources=self._build_sources(chunks_with_scores),
            retrieved_chunks=len(chunks_with_scores),
            generation_time=generation_time,
        )

        session = ConversationSession()
        session.add_user_message(request.text)
        session.add_assistant_message(answer, query_result)

        return QueryResponse(
            id=query_result.id,
            session_id=session.id,
            answer=answer,
            sources=self._build_sources(chunks_with_scores),
            retrieved_chunks=len(chunks_with_scores),
            generation_time=generation_time,
            created_at=query_result.created_at,
        )

    async def query_with_history(
        self,
        request: RAGQueryRequest,
        collection_name: str = "knowledge_base",
    ) -> QueryResponse:
        """处理带历史的多轮对话查询"""
        start_time = time.time()
        pipeline = self.pipeline_factory.create(
            embedding_client=self.embedding_client,
            reranker_client=self.reranker_client,
            collection_name=collection_name,
            retrieval_strategy=request.retrieval_strategy,
            query_processing_strategy=request.query_processing_strategy,
            reranking_strategy=request.reranking_strategy,
            context_assembly_strategy=request.context_assembly_strategy,
        )

        # 1. 向量化查询
        query_vector = await pipeline.query_processor.embed(request.text)

        # 2. 检索相关切片
        chunks_with_scores = await pipeline.retriever.retrieve(
            query_text=request.text,
            query_vector=query_vector,
            top_k=request.top_k,
            filters=request.filters,
        )

        if not chunks_with_scores:
            raise NoRelevantChunksError(request.text)

        # 3. Rerank（如果启用）
        chunks_with_scores = await pipeline.reranker.rerank(
            query=request.text,
            chunks=chunks_with_scores,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
        )

        # 4. 构建上下文
        context = pipeline.context_builder.build(chunks_with_scores)

        # 5. 生成回答（带历史）
        answer = await self._generate_answer_with_history(
            query=request.text,
            context=context,
            chunks=chunks_with_scores,
            history=request.history,
        )

        generation_time = time.time() - start_time
        query_result = QueryResult(
            id=str(uuid4()),
            query_id="",
            answer=answer,
            sources=self._build_sources(chunks_with_scores),
            retrieved_chunks=len(chunks_with_scores),
            generation_time=generation_time,
        )

        return QueryResponse(
            id=query_result.id,
            session_id=request.session_id or "",
            answer=answer,
            sources=query_result.sources,
            retrieved_chunks=query_result.retrieved_chunks,
            generation_time=query_result.generation_time,
            created_at=query_result.created_at,
        )

    async def _generate_answer(
        self,
        query: str,
        context: str,
        chunks: List[ChunkWithScore],
    ) -> str:
        """生成回答（单轮）"""
        messages = [
            {
                "role": "user",
                "content": self._build_prompt(query, context),
            }
        ]

        try:
            return await self.llm_client.chat(
                messages=messages,
                system_prompt=self.DEFAULT_SYSTEM_PROMPT,
            )
        except LLMError as e:
            logger.error(f"生成回答失败: {e}")
            return self._build_fallback_answer(query, chunks)

    async def _generate_answer_with_history(
        self,
        query: str,
        context: str,
        chunks: List[ChunkWithScore],
        history: list[HistoryMessage],
    ) -> str:
        """生成回答（多轮）"""
        # 构建历史消息
        chat_messages = []
        for msg in history:
            chat_messages.append({"role": msg.role, "content": msg.content})

        # 当前轮：把上下文和问题合并
        chat_messages.append({
            "role": "user",
            "content": self._build_prompt(query, context),
        })

        try:
            return await self.llm_client.chat(
                messages=chat_messages,
                system_prompt=self.DEFAULT_SYSTEM_PROMPT,
            )
        except LLMError as e:
            logger.error(f"生成回答失败: {e}")
            return self._build_fallback_answer(query, chunks)

    def _build_prompt(self, query: str, context: str) -> str:
        """构建用户消息 prompt"""
        return f"""基于以下知识库内容回答问题。如果知识库中没有相关信息，请如实告知。

知识库内容：
{context}

问题：{query}

回答："""

    def _build_fallback_answer(
        self,
        query: str,
        chunks: List[ChunkWithScore],
    ) -> str:
        """后备回答"""
        if not chunks:
            return "抱歉，未找到与您问题相关的内容。"

        top_chunks = chunks[:3]
        answer_parts = ["根据检索到的内容，以下是相关信息：\n"]

        for i, chunk_with_score in enumerate(top_chunks, 1):
            content_preview = chunk_with_score.chunk.content[:200]
            answer_parts.append(f"\n{i}. {content_preview}...")

        return "".join(answer_parts)

    def _build_sources(self, chunks: List[ChunkWithScore]) -> List[Dict[str, Any]]:
        """构建来源信息"""
        sources = []
        seen_docs = set()

        for chunk_with_score in chunks:
            chunk = chunk_with_score.chunk
            doc_key = chunk.document_id

            if doc_key not in seen_docs:
                seen_docs.add(doc_key)
                sources.append({
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "content_preview": chunk.content[:100],
                    "score": chunk_with_score.score,
                })

        return sources


__all__ = ["RAGService"]

