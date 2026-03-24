"""检索器插件接口"""
from abc import abstractmethod
from typing import List, Protocol, runtime_checkable, Optional

from .base import PluginConfig, PluginRegistry
from ..entities.chunk import ChunkWithScore


class RetrieverConfig(PluginConfig):
    """检索器配置"""
    top_k: int = 5


@runtime_checkable
class RetrieverPlugin(Protocol):
    """检索器插件接口
    
    所有检索器都应该实现这个接口
    """
    
    name: str
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: dict = None,
        **kwargs
    ) -> List[ChunkWithScore]:
        """检索相关切片
        
        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件
            **kwargs: 其他参数
            
        Returns:
            相关切片列表（带分数）
        """
        ...
    
    async def aretrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: dict = None,
        **kwargs
    ) -> List[ChunkWithScore]:
        """异步检索相关切片"""
        return self.retrieve(query, top_k, filters, **kwargs)


def register_retriever(name: str = None):
    """检索器注册装饰器"""
    return PluginRegistry.register("retriever", name)


__all__ = [
    "RetrieverConfig",
    "RetrieverPlugin",
    "register_retriever",
]
