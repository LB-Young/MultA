"""PDF 文档提取器"""
from pathlib import Path

from src.domain.plugins import ExtractorConfig
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class PDFExtractorConfig(ExtractorConfig):
    """PDF 提取器配置"""
    supported_extensions: list[str] = [".pdf"]


class PDFExtractor:
    """PDF 文档提取器"""
    
    name = "pdf"
    supported_extensions = [".pdf"]
    
    def __init__(self, config: PDFExtractorConfig = None):
        self.config = config or PDFExtractorConfig(name="pdf")
        self._pypdf = None
    
    def _load_pypdf(self):
        """延迟加载 pypdf 库"""
        if self._pypdf is None:
            try:
                from pypdf import PdfReader
                self._pypdf = PdfReader
            except ImportError:
                raise ImportError("请安装 pypdf: pip install pypdf")
    
    def extract(self, file_path: Path) -> str:
        """提取 PDF 文档内容"""
        try:
            self._load_pypdf()
            
            reader = self._pypdf(str(file_path))
            pages = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages.append(f"[第 {page_num + 1} 页]\n{text}")
            
            content = "\n\n".join(pages)
            logger.debug(f"成功提取 PDF 文档: {file_path}, 页数: {len(reader.pages)}")
            return content
            
        except Exception as e:
            raise ValueError(f"提取 PDF 文档失败: {file_path} - {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取"""
        return file_path.suffix.lower() in self.supported_extensions
