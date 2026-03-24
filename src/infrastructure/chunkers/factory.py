"""切片器工厂"""
from typing import Optional

from src.domain.plugins import PluginRegistry
from src.infrastructure.logging.setup import get_logger


logger = get_logger(__name__)


class ChunkerFactory:
    """切片器工厂"""
    
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, config: dict = None) -> None:
        """初始化切片器注册"""
        if cls._initialized:
            return
        
        from src.infrastructure.chunkers.registry import register_all_chunkers
        register_all_chunkers()
        cls._initialized = True
        
        chunkers = PluginRegistry.list_plugins("chunker")
        logger.info(f"已注册 {len(chunkers)} 个切片器: {chunkers}")
    
    @classmethod
    def get_chunker(
        cls,
        strategy: str = "fixed_chars",
        chunk_size: int = 500,
        overlap: int = 50,
        **kwargs,
    ):
        """获取切片器

        Args:
            strategy: 切片策略
            chunk_size: 块大小
            overlap: 重叠大小
            **kwargs: 其他参数

        Returns:
            切片器实例
        """
        cls.initialize()

        try:
            # PluginRegistry.get 返回的是类，不是实例
            # 我们需要手动实例化并传递参数
            chunker_cls = PluginRegistry._plugins.get("chunker", {}).get(strategy)
            if chunker_cls is None:
                raise ValueError(f"切片器 {strategy} 未注册")

            # 根据策略类型创建实例
            if strategy == "fixed_chars":
                return chunker_cls(
                    chunk_size=chunk_size,
                    overlap=overlap,
                    min_chunk_size=kwargs.get("min_chunk_size", 50),
                )
            elif strategy == "fixed_tokens":
                return chunker_cls(
                    chunk_size=chunk_size,
                    overlap=overlap,
                    min_chunk_size=kwargs.get("min_chunk_size", 50),
                    encoding_name=kwargs.get("encoding_name", "cl100k_base"),
                )
            else:
                return chunker_cls()

        except Exception as e:
            logger.warning(f"获取切片器失败，使用默认: {e}")
            from src.infrastructure.chunkers.fixed_chars import FixedCharsChunker
            return FixedCharsChunker(chunk_size=chunk_size, overlap=overlap)
    
    @classmethod
    def list_chunkers(cls) -> list[str]:
        """列出所有可用的切片器"""
        cls.initialize()
        return PluginRegistry.list_plugins("chunker")


__all__ = ["ChunkerFactory"]
