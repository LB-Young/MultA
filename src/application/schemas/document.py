"""文档相关 Schema"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    message: str = "文件上传成功"


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    items: list[dict]
    total: int
    skip: int
    limit: int


class DocumentProcessRequest(BaseModel):
    """文档处理请求"""
    chunk_size: int = Field(default=500, ge=100, le=5000)
    overlap: int = Field(default=50, ge=0, le=1000)
    strategy: str = Field(default="fixed_chars")


class DocumentProcessResponse(BaseModel):
    """文档处理响应"""
    id: str
    status: str
    text_length: int
    chunk_count: int
    message: str = "文档处理成功"


__all__ = [
    "DocumentUploadResponse",
    "DocumentListResponse",
    "DocumentProcessRequest",
    "DocumentProcessResponse",
]
