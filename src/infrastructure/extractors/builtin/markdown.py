"""Markdown 提取器"""
from pathlib import Path

from src.domain.plugins import ExtractorConfig
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class MarkdownExtractorConfig(ExtractorConfig):
    """Markdown 提取器配置"""
    supported_extensions: list[str] = [".md", ".markdown"]


class MarkdownExtractor:
    """Markdown 文件提取器"""
    
    name = "markdown"
    supported_extensions = [".md", ".markdown"]
    
    def __init__(self, config: MarkdownExtractorConfig = None):
        self.config = config or MarkdownExtractorConfig(name="markdown")
    
    def extract(self, file_path: Path) -> str:
        """提取 Markdown 内容"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.debug(f"成功提取 Markdown 文件: {file_path}")
            return content
        except Exception as e:
            raise ValueError(f"提取 Markdown 文件失败: {file_path} - {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取"""
        return file_path.suffix.lower() in self.supported_extensions
