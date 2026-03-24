"""文档实体测试"""
import pytest
from src.domain.entities.document import Document, DocumentStatus, DocumentType


class TestDocument:
    """文档实体测试"""
    
    def test_create_document(self):
        """测试创建文档"""
        doc = Document(
            filename="test.txt",
            original_filename="原始文件.txt",
            file_path=Path("data/uploads/test.txt"),
            file_size=1024,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            extension=".txt",
        )
        
        assert doc.filename == "test.txt"
        assert doc.status == DocumentStatus.UPLOADED
        assert doc.id is not None
    
    def test_mark_processing(self):
        """测试标记为处理中"""
        doc = Document(
            filename="test.txt",
            original_filename="test.txt",
            file_path=Path("test.txt"),
            file_size=1024,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            extension=".txt",
        )
        
        doc.mark_processing()
        
        assert doc.status == DocumentStatus.PROCESSING
    
    def test_mark_processed(self):
        """测试标记为已处理"""
        doc = Document(
            filename="test.txt",
            original_filename="test.txt",
            file_path=Path("test.txt"),
            file_size=1024,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            extension=".txt",
        )
        
        doc.mark_processed(text_length=500, chunk_count=5)
        
        assert doc.status == DocumentStatus.PROCESSED
        assert doc.text_length == 500
        assert doc.chunk_count == 5
    
    def test_mark_failed(self):
        """测试标记为失败"""
        doc = Document(
            filename="test.txt",
            original_filename="test.txt",
            file_path=Path("test.txt"),
            file_size=1024,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            extension=".txt",
        )
        
        doc.mark_failed("测试错误")
        
        assert doc.status == DocumentStatus.FAILED
        assert doc.error_message == "测试错误"


from pathlib import Path
