"""文档领域实体"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """文档状态"""
    UPLOADED = "uploaded"      # 已上传
    PROCESSING = "processing"  # 处理中
    PROCESSED = "processed"   # 已处理
    FAILED = "failed"          # 处理失败


class DocumentType(str, Enum):
    """文档类型"""
    TEXT = "text"              # 纯文本
    WORD = "word"             # Word 文档
    EXCEL = "excel"           # Excel 表格
    PDF = "pdf"               # PDF 文档
    MARKDOWN = "markdown"     # Markdown
    IMAGE = "image"           # 图片
    AUDIO = "audio"           # 音频
    OTHER = "other"           # 其他


class Document(BaseModel):
    """文档实体"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    original_filename: str
    file_path: Path
    file_size: int
    file_type: DocumentType
    mime_type: str
    extension: str
    status: DocumentStatus = DocumentStatus.UPLOADED
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
    
    # 处理信息
    text_length: int = 0
    chunk_count: int = 0
    
    class Config:
        arbitrary_types_allowed = True
    
    def mark_processing(self) -> None:
        """标记为处理中"""
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.now()
    
    def mark_processed(self, text_length: int, chunk_count: int) -> None:
        """标记为已处理"""
        self.status = DocumentStatus.PROCESSED
        self.text_length = text_length
        self.chunk_count = chunk_count
        self.updated_at = datetime.now()
    
    def mark_failed(self, error_message: str) -> None:
        """标记为失败"""
        self.status = DocumentStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now()
    
    @property
    def is_processed(self) -> bool:
        """是否已处理"""
        return self.status == DocumentStatus.PROCESSED
    
    @property
    def is_failed(self) -> bool:
        """是否处理失败"""
        return self.status == DocumentStatus.FAILED


class DocumentCreate(BaseModel):
    """创建文档请求"""
    filename: str
    file_size: int
    file_type: DocumentType
    mime_type: str
    extension: str


class DocumentResponse(BaseModel):
    """文档响应"""
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    text_length: int
    chunk_count: int
    created_at: datetime
    updated_at: datetime


__all__ = [
    "Document",
    "DocumentStatus",
    "DocumentType",
    "DocumentCreate",
    "DocumentResponse",
]
