"""内置提取器注册"""
from .txt import TxtExtractor
from .docx import DocxExtractor
from .pdf import PDFExtractor
from .xlsx import XlsxExtractor
from .pptx import PptxExtractor
from .markdown import MarkdownExtractor

# 全局注册所有内置提取器
def register_all_extractors():
    """注册所有内置提取器"""
    from src.domain.plugins import PluginRegistry
    
    # 注册每个提取器
    PluginRegistry.register("extractor", "txt")(TxtExtractor)
    PluginRegistry.register("extractor", "md")(MarkdownExtractor)
    PluginRegistry.register("extractor", "json")(TxtExtractor)  # JSON 也用文本提取器
    PluginRegistry.register("extractor", "docx")(DocxExtractor)
    PluginRegistry.register("extractor", "pdf")(PDFExtractor)
    PluginRegistry.register("extractor", "xlsx")(XlsxExtractor)
    PluginRegistry.register("extractor", "pptx")(PptxExtractor)
    
    return {
        "txt": TxtExtractor,
        "md": MarkdownExtractor,
        "json": TxtExtractor,
        "docx": DocxExtractor,
        "pdf": PDFExtractor,
        "xlsx": XlsxExtractor,
        "pptx": PptxExtractor,
    }


__all__ = [
    "TxtExtractor",
    "DocxExtractor",
    "PDFExtractor",
    "XlsxExtractor",
    "PptxExtractor",
    "MarkdownExtractor",
    "register_all_extractors",
]
