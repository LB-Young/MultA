"""异常测试"""
import pytest
from src.infrastructure.exceptions import (
    FileSystemError,
    DocumentNotFoundError,
    UnsupportedFileTypeError,
    ExtractionError,
)


class TestExceptions:
    """异常测试"""
    
    def test_filesystem_error(self):
        """测试基础异常"""
        error = FileSystemError(
            message="测试错误",
            code="TEST_ERROR",
            details={"key": "value"},
        )
        
        assert str(error) == "测试错误"
        assert error.code == "TEST_ERROR"
        assert error.details["key"] == "value"
        
        # 测试 to_dict
        error_dict = error.to_dict()
        assert "error" in error_dict
        assert error_dict["error"]["code"] == "TEST_ERROR"
    
    def test_document_not_found(self):
        """测试文档未找到异常"""
        error = DocumentNotFoundError("doc-123")
        
        assert "doc-123" in str(error)
        assert error.code == "DOCUMENT_NOT_FOUND"
    
    def test_unsupported_file_type(self):
        """测试不支持的文件类型异常"""
        error = UnsupportedFileTypeError(".xyz")
        
        assert ".xyz" in str(error)
        assert error.code == "UNSUPPORTED_FILE_TYPE"
    
    def test_exception_hierarchy(self):
        """测试异常层次"""
        error = ExtractionError("提取失败")
        
        assert isinstance(error, FileSystemError)
