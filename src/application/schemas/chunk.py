"""切片相关 Schema"""
from pydantic import BaseModel


class ChunkListResponse(BaseModel):
    """切片列表响应"""
    document_id: str
    chunks: list[dict]
    total: int


__all__ = ["ChunkListResponse"]
