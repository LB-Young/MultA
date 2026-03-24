"""提取器插件接口"""
from abc import abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable, List

from .base import PluginConfig, PluginRegistry


class ExtractorConfig(PluginConfig):
    """提取器配置"""
    supported_extensions: List[str] = []


@runtime_checkable
class ExtractorPlugin(Protocol):
    """提取器插件接口
    
    所有文件提取器都应该实现这个接口
    """
    
    name: str
    supported_extensions: List[str]
    
    def extract(self, file_path: Path) -> str:
        """提取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
            
        Raises:
            ExtractionFailedError: 提取失败
        """
        ...
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否可以提取
        """
        ...


def register_extractor(name: str = None):
    """提取器注册装饰器
    
    用法:
        @register_extractor("pdf")
        class PDFExtractor:
            name = "pdf"
            supported_extensions = [".pdf"]
            
            def extract(self, file_path: Path) -> str:
                ...
    """
    return PluginRegistry.register("extractor", name)


__all__ = [
    "ExtractorConfig",
    "ExtractorPlugin",
    "register_extractor",
]
