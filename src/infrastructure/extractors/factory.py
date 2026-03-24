"""提取器工厂"""
from pathlib import Path
from typing import Optional

from src.domain.plugins import PluginRegistry
from src.domain.entities.document import DocumentType
from src.infrastructure.exceptions import ExtractorNotFoundError
from src.infrastructure.logging.setup import get_logger


logger = get_logger(__name__)


class ExtractorFactory:
    """提取器工厂
    
    根据文件类型创建对应的提取器
    """
    
    # 文件类型到提取器名称的映射
    TYPE_TO_EXTRACTOR: dict[str, str] = {
        "text": "txt",
        "word": "docx",
        "excel": "xlsx",
        "pdf": "pdf",
        "markdown": "md",
    }
    
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> None:
        """初始化提取器注册"""
        # 每次都重新注册，确保插件可用
        from src.infrastructure.extractors.builtin.registry import register_all_extractors
        register_all_extractors()
        cls._initialized = True

        # 记录已注册的提取器
        extractors = PluginRegistry.list_plugins("extractor")
        logger.info(f"已注册 {len(extractors)} 个提取器: {extractors}")
    
    @classmethod
    def get_extractor(
        cls,
        file_type: str | DocumentType,
        extension: str = None,
    ):
        """获取提取器

        Args:
            file_type: 文件类型或 DocumentType
            extension: 文件扩展名（可选）

        Returns:
            提取器实例

        Raises:
            ExtractorNotFoundError: 未找到合适的提取器
        """
        cls.initialize()

        # 确定提取器名称
        if isinstance(file_type, DocumentType):
            file_type = file_type.value

        extractor_name = cls.TYPE_TO_EXTRACTOR.get(file_type)

        # 如果映射表中没有，尝试使用传入的值
        if extractor_name is None:
            extractor_name = file_type

        # 如果指定了扩展名，优先使用
        if extension:
            extractor_name = extension.lstrip(".")

        if extractor_name is None:
            raise ExtractorNotFoundError(file_type)

        try:
            return PluginRegistry.get("extractor", extractor_name)
        except Exception:
            raise ExtractorNotFoundError(extractor_name)
    
    @classmethod
    def extract_file(cls, file_path: Path, file_type: str | DocumentType = None) -> str:
        """提取文件内容
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            提取的文本内容
        """
        if file_type is None:
            file_type = file_path.suffix.lstrip(".")
        
        extractor = cls.get_extractor(file_type)
        return extractor.extract(file_path)
    
    @classmethod
    def list_extractors(cls) -> list[str]:
        """列出所有可用的提取器"""
        cls.initialize()
        return PluginRegistry.list_plugins("extractor")


__all__ = ["ExtractorFactory"]
