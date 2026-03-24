"""切片器注册"""
from .fixed_chars import FixedCharsChunker
from .fixed_tokens import FixedTokensChunker


def register_all_chunkers():
    """注册所有内置切片器"""
    from src.domain.plugins import PluginRegistry
    
    PluginRegistry.register("chunker", "fixed_chars")(FixedCharsChunker)
    PluginRegistry.register("chunker", "fixed_tokens")(FixedTokensChunker)
    
    return {
        "fixed_chars": FixedCharsChunker,
        "fixed_tokens": FixedTokensChunker,
    }


__all__ = [
    "FixedCharsChunker",
    "FixedTokensChunker",
    "register_all_chunkers",
]
