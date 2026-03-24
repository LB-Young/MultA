"""紧凑上下文拼接策略。"""
from src.domain.entities.chunk import ChunkWithScore

from .base import BaseContextBuilder


class CompactContextBuilder(BaseContextBuilder):
    strategy_name = "compact"

    def __init__(self, max_chars_per_chunk: int = 280):
        self.max_chars_per_chunk = max_chars_per_chunk

    def build(self, chunks: list[ChunkWithScore]) -> str:
        context_parts = []
        for i, chunk_with_score in enumerate(chunks, 1):
            chunk = chunk_with_score.chunk
            content = chunk.content[: self.max_chars_per_chunk]
            context_parts.append(f"[文档{i}]\n{content}")
        return "\n\n".join(context_parts)
