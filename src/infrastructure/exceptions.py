"""统一异常体系"""
from typing import Any, Optional


class FileSystemError(Exception):
    """系统基础异常"""
    
    def __init__(
        self,
        message: str,
        code: str = "SYSTEM_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# 文档相关异常
class DocumentError(FileSystemError):
    """文档基础异常"""
    pass


class DocumentNotFoundError(DocumentError):
    """文档不存在"""
    
    def __init__(self, document_id: str):
        super().__init__(
            message=f"文档不存在: {document_id}",
            code="DOCUMENT_NOT_FOUND",
            details={"document_id": document_id},
        )


class DocumentAlreadyExistsError(DocumentError):
    """文档已存在"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"文档已存在: {filename}",
            code="DOCUMENT_ALREADY_EXISTS",
            details={"filename": filename},
        )


class FileReadError(DocumentError):
    """文件读取失败"""
    
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"文件读取失败: {filename} - {reason}",
            code="FILE_READ_ERROR",
            details={"filename": filename, "reason": reason},
        )


class UnsupportedFileTypeError(DocumentError):
    """不支持的文件类型"""
    
    def __init__(self, extension: str):
        super().__init__(
            message=f"不支持的文件类型: {extension}",
            code="UNSUPPORTED_FILE_TYPE",
            details={"extension": extension},
        )


class FileTooLargeError(DocumentError):
    """文件过大"""
    
    def __init__(self, filename: str, size: int, max_size: int):
        super().__init__(
            message=f"文件过大: {filename} ({size} bytes > {max_size} bytes)",
            code="FILE_TOO_LARGE",
            details={"filename": filename, "size": size, "max_size": max_size},
        )


# 提取相关异常
class ExtractionError(FileSystemError):
    """文档提取基础异常"""
    pass


class ExtractionFailedError(ExtractionError):
    """文档内容提取失败"""
    
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"文档内容提取失败: {filename} - {reason}",
            code="EXTRACTION_FAILED",
            details={"filename": filename, "reason": reason},
        )


class ExtractorNotFoundError(ExtractionError):
    """未找到合适的提取器"""
    
    def __init__(self, extension: str):
        super().__init__(
            message=f"未找到适用于 {extension} 的提取器",
            code="EXTRACTOR_NOT_FOUND",
            details={"extension": extension},
        )


# 切片相关异常
class ChunkingError(FileSystemError):
    """切片基础异常"""
    pass


class ChunkingFailedError(ChunkingError):
    """切片处理失败"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"切片处理失败: {reason}",
            code="CHUNKING_FAILED",
            details={"reason": reason},
        )


class EmptyContentError(ChunkingError):
    """文档内容为空"""
    
    def __init__(self, document_id: str):
        super().__init__(
            message=f"文档内容为空: {document_id}",
            code="EMPTY_CONTENT",
            details={"document_id": document_id},
        )


# 向量相关异常
class VectorizationError(FileSystemError):
    """向量化基础异常"""
    pass


class EmbeddingFailedError(VectorizationError):
    """Embedding 生成失败"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Embedding 生成失败: {reason}",
            code="EMBEDDING_FAILED",
            details={"reason": reason},
        )


class VectorStoreError(FileSystemError):
    """向量存储基础异常"""
    pass


class CollectionNotFoundError(VectorStoreError):
    """向量集合不存在"""
    
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"向量集合不存在: {collection_name}",
            code="COLLECTION_NOT_FOUND",
            details={"collection_name": collection_name},
        )


class VectorStoreConnectionError(VectorStoreError):
    """向量数据库连接失败"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"向量数据库连接失败: {reason}",
            code="VECTOR_STORE_CONNECTION_ERROR",
            details={"reason": reason},
        )


# RAG 相关异常
class RAGError(FileSystemError):
    """RAG 基础异常"""
    pass


class QueryError(RAGError):
    """查询处理失败"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"查询处理失败: {reason}",
            code="QUERY_ERROR",
            details={"reason": reason},
        )


class LLMError(RAGError):
    """LLM 调用失败"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"LLM 调用失败: {reason}",
            code="LLM_ERROR",
            details={"reason": reason},
        )


class NoRelevantChunksError(RAGError):
    """未找到相关切片"""
    
    def __init__(self, query: str):
        super().__init__(
            message=f"未找到与查询相关的切片: {query}",
            code="NO_RELEVANT_CHUNKS",
            details={"query": query},
        )


# 配置相关异常
class ConfigError(FileSystemError):
    """配置基础异常"""
    pass


class ConfigNotFoundError(ConfigError):
    """配置文件不存在"""
    
    def __init__(self, path: str):
        super().__init__(
            message=f"配置文件不存在: {path}",
            code="CONFIG_NOT_FOUND",
            details={"path": path},
        )


class InvalidConfigError(ConfigError):
    """配置无效"""
    
    def __init__(self, key: str, reason: str):
        super().__init__(
            message=f"配置无效: {key} - {reason}",
            code="INVALID_CONFIG",
            details={"key": key, "reason": reason},
        )


# 插件相关异常
class PluginError(FileSystemError):
    """插件基础异常"""
    pass


class PluginNotFoundError(PluginError):
    """插件未找到"""
    
    def __init__(self, plugin_type: str, name: str):
        super().__init__(
            message=f"插件未找到: {plugin_type}/{name}",
            code="PLUGIN_NOT_FOUND",
            details={"plugin_type": plugin_type, "name": name},
        )


class PluginRegistrationError(PluginError):
    """插件注册失败"""
    
    def __init__(self, name: str, reason: str):
        super().__init__(
            message=f"插件注册失败: {name} - {reason}",
            code="PLUGIN_REGISTRATION_ERROR",
            details={"name": name, "reason": reason},
        )


__all__ = [
    "FileSystemError",
    # 文档异常
    "DocumentError",
    "DocumentNotFoundError",
    "DocumentAlreadyExistsError",
    "FileReadError",
    "UnsupportedFileTypeError",
    "FileTooLargeError",
    # 提取异常
    "ExtractionError",
    "ExtractionFailedError",
    "ExtractorNotFoundError",
    # 切片异常
    "ChunkingError",
    "ChunkingFailedError",
    "EmptyContentError",
    # 向量异常
    "VectorizationError",
    "EmbeddingFailedError",
    "VectorStoreError",
    "CollectionNotFoundError",
    "VectorStoreConnectionError",
    # RAG 异常
    "RAGError",
    "QueryError",
    "LLMError",
    "NoRelevantChunksError",
    # 配置异常
    "ConfigError",
    "ConfigNotFoundError",
    "InvalidConfigError",
    # 插件异常
    "PluginError",
    "PluginNotFoundError",
    "PluginRegistrationError",
]
