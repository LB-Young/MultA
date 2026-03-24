"""Word 文档提取器"""
from pathlib import Path

from src.domain.plugins import ExtractorConfig
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class DocxExtractorConfig(ExtractorConfig):
    """Docx 提取器配置"""
    supported_extensions: list[str] = [".docx"]


class DocxExtractor:
    """Word 文档提取器"""
    
    name = "docx"
    supported_extensions = [".docx"]
    
    def __init__(self, config: DocxExtractorConfig = None):
        self.config = config or DocxExtractorConfig(name="docx")
        self._docx = None
    
    def _load_docx(self):
        """延迟加载 docx 库"""
        if self._docx is None:
            try:
                from docx import Document
                self._docx = Document
            except ImportError:
                raise ImportError("请安装 python-docx: pip install python-docx")
    
    def extract(self, file_path: Path) -> str:
        """提取 Word 文档内容"""
        try:
            self._load_docx()
            
            doc = self._docx(str(file_path))
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            # 提取表格
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip("|"):
                        paragraphs.append(row_text)
            
            content = "\n".join(paragraphs)
            logger.debug(f"成功提取 Word 文档: {file_path}, 段落数: {len(paragraphs)}")
            return content
            
        except Exception as e:
            raise ValueError(f"提取 Word 文档失败: {file_path} - {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取"""
        return file_path.suffix.lower() in self.supported_extensions
