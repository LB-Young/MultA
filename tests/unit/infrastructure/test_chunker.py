"""切片器测试"""
import pytest
from src.infrastructure.chunkers.fixed_chars import FixedCharsChunker


class TestFixedCharsChunker:
    """固定字符切片器测试"""
    
    def test_basic_chunking(self, sample_text):
        """测试基本切片"""
        chunker = FixedCharsChunker(chunk_size=50, overlap=10)
        
        chunks = chunker.chunk(sample_text, document_id="test-doc")
        
        assert len(chunks) > 0
        assert all(chunk.document_id == "test-doc" for chunk in chunks)
        assert all(chunk.length > 0 for chunk in chunks)
    
    def test_empty_text(self):
        """测试空文本"""
        chunker = FixedCharsChunker()
        
        chunks = chunker.chunk("", document_id="test")
        
        assert len(chunks) == 0
    
    def test_short_text(self):
        """测试短文本"""
        chunker = FixedCharsChunker(chunk_size=100)
        
        chunks = chunker.chunk("短文本", document_id="test")
        
        assert len(chunks) == 1
        assert chunks[0].content == "短文本"
    
    def test_chunk_metadata(self, sample_text):
        """测试切片元数据"""
        chunker = FixedCharsChunker(chunk_size=50, overlap=10)
        
        chunks = chunker.chunk(sample_text, document_id="test-doc")
        
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
