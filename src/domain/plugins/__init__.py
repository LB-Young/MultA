"""插件系统"""
from .base import PluginConfig, PluginRegistry, PluginBase
from .extractor import ExtractorConfig, ExtractorPlugin, register_extractor
from .chunker import ChunkerConfig, ChunkerPlugin, register_chunker
from .retriever import RetrieverConfig, RetrieverPlugin, register_retriever

__all__ = [
    "PluginConfig",
    "PluginRegistry",
    "PluginBase",
    "ExtractorConfig",
    "ExtractorPlugin",
    "register_extractor",
    "ChunkerConfig",
    "ChunkerPlugin",
    "register_chunker",
    "RetrieverConfig",
    "RetrieverPlugin",
    "register_retriever",
]
