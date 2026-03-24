"""纯文本提取器"""
from pathlib import Path

from src.domain.plugins import ExtractorConfig, ExtractorPlugin
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class TxtExtractorConfig(ExtractorConfig):
    """TXT 提取器配置"""
    supported_extensions: list[str] = [".txt", ".json"]


class TxtExtractor:
    """纯文本文件提取器"""
    
    name = "txt"
    supported_extensions = [".txt", ".json"]
    
    def __init__(self, config: TxtExtractorConfig = None):
        self.config = config or TxtExtractorConfig(name="txt")
    
    def extract(self, file_path: Path) -> str:
        """提取文本内容"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.debug(f"成功提取文本文件: {file_path}, 长度: {len(content)}")
            return content
        except UnicodeDecodeError:
            # 尝试其他编码
            for encoding in ["gbk", "gb2312", "latin1"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    logger.debug(f"使用 {encoding} 编码成功提取: {file_path}")
                    return content
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"无法解码文件: {file_path}")
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取"""
        return file_path.suffix.lower() in self.supported_extensions
