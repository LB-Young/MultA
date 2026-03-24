"""标准上下文拼接策略。"""
from src.domain.entities.chunk import ChunkWithScore

from .base import BaseContextBuilder


class StandardContextBuilder(BaseContextBuilder):
    strategy_name = "standard"

    def build(self, chunks: list[ChunkWithScore]) -> str:
        context_parts = []
        for i, chunk_with_score in enumerate(chunks, 1):
            chunk = chunk_with_score.chunk
            context_parts.append(f"[文档{i}]\n{chunk.content}")
        return "\n\n".join(context_parts)
