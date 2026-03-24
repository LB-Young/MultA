"""切片器插件接口"""
from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from .base import PluginConfig, PluginRegistry
from ..entities.chunk import Chunk


class ChunkerConfig(PluginConfig):
    """切片器配置"""
    chunk_size: int = 500
    overlap: int = 50
    min_chunk_size: int = 50


@runtime_checkable
class ChunkerPlugin(Protocol):
    """切片器插件接口
    
    所有文本切片器都应该实现这个接口
    """
    
    name: str
    
    def chunk(self, text: str, document_id: str = None, **kwargs) -> List[Chunk]:
        """将文本切分为块
        
        Args:
            text: 输入文本
            document_id: 文档 ID
            **kwargs: 其他参数
            
        Returns:
            切片列表
            
        Raises:
            ChunkingFailedError: 切片失败
        """
        ...


def register_chunker(name: str = None):
    """切片器注册装饰器
    
    用法:
        @register_chunker("fixed_chars")
        class FixedCharsChunker:
            name = "fixed_chars"
            
            def chunk(self, text: str, document_id: str = None, **kwargs) -> List[Chunk]:
                ...
    """
    return PluginRegistry.register("chunker", name)


__all__ = [
    "ChunkerConfig",
    "ChunkerPlugin",
    "register_chunker",
]
