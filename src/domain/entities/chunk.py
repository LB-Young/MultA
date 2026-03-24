"""切片领域实体"""
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """切片实体"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    content: str
    chunk_index: int  # 在文档中的位置
    start_char: int   # 开始字符位置
    end_char: int     # 结束字符位置
    length: int        # 字符长度
    vector_id: Optional[str] = None  # 向量数据库中的 ID
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 质量指标
    quality_score: float = 0.0
    
    def __init__(self, **data):
        if "content" in data:
            data["length"] = len(data["content"])
        super().__init__(**data)
    
    @property
    def is_vectorized(self) -> bool:
        """是否已向量化"""
        return self.vector_id is not None
    
    def set_vector_id(self, vector_id: str) -> None:
        """设置向量 ID"""
        self.vector_id = vector_id


class ChunkWithScore(BaseModel):
    """带分数的切片"""
    chunk: Chunk
    score: float
    rank: int = 0


class ChunkResponse(BaseModel):
    """切片响应"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    length: int
    score: Optional[float] = None


__all__ = [
    "Chunk",
    "ChunkWithScore",
    "ChunkResponse",
]
