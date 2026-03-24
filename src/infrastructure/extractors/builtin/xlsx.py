"""Excel 提取器"""
from pathlib import Path

from src.domain.plugins import ExtractorConfig
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class XlsxExtractorConfig(ExtractorConfig):
    """Excel 提取器配置"""
    supported_extensions: list[str] = [".xlsx", ".xls"]


class XlsxExtractor:
    """Excel 表格提取器"""
    
    name = "xlsx"
    supported_extensions = [".xlsx", ".xls"]
    
    def __init__(self, config: XlsxExtractorConfig = None):
        self.config = config or XlsxExtractorConfig(name="xlsx")
        self._openpyxl = None
    
    def _load_openpyxl(self):
        """延迟加载 openpyxl 库"""
        if self._openpyxl is None:
            try:
                from openpyxl import load_workbook
                self._openpyxl = load_workbook
            except ImportError:
                raise ImportError("请安装 openpyxl: pip install openpyxl")
    
    def extract(self, file_path: Path) -> str:
        """提取 Excel 表格内容"""
        try:
            self._load_openpyxl()
            
            workbook = self._openpyxl(str(file_path), data_only=True)
            paragraphs = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                paragraphs.append(f"[Sheet: {sheet_name}]")
                
                # 提取表头（第一行）
                headers = []
                for cell in sheet[1]:
                    if cell.value:
                        headers.append(str(cell.value))
                
                if headers:
                    paragraphs.append("表头: " + " | ".join(headers))
                
                # 提取数据行
                for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    row_values = [str(v) if v is not None else "" for v in row]
                    if any(row_values):
                        paragraphs.append(f"行{row_idx}: " + " | ".join(row_values))
                
                paragraphs.append("")  # 空行分隔
            
            content = "\n".join(paragraphs)
            logger.debug(f"成功提取 Excel 文件: {file_path}, Sheet 数: {len(workbook.sheetnames)}")
            return content
            
        except Exception as e:
            raise ValueError(f"提取 Excel 文件失败: {file_path} - {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否可以被提取"""
        return file_path.suffix.lower() in self.supported_extensions
