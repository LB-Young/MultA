"""固定字符数切片器"""
from typing import List

from src.domain.entities.chunk import Chunk
from src.domain.plugins import ChunkerConfig, ChunkerPlugin
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class FixedCharsChunkerConfig(ChunkerConfig):
    """固定字符切片器配置"""
    name: str = "fixed_chars"
    chunk_size: int = 500
    overlap: int = 50
    min_chunk_size: int = 50


class FixedCharsChunker:
    """固定字符数切片器
    
    将文本按固定字符数切分，相邻块之间有重叠
    """
    
    name = "fixed_chars"
    
    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        min_chunk_size: int = 50,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str, document_id: str = None, **kwargs) -> List[Chunk]:
        """将文本切分为固定大小的块
        
        Args:
            text: 输入文本
            document_id: 文档 ID
            
        Returns:
            切片列表
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 尝试在句子边界处分割
            if end < len(text):
                # 向前查找最后一个句子边界
                for sep in ["。", "！", "？", "\n", "，", "；"]:
                    last_sep = text.rfind(sep, start + self.chunk_size // 2, end)
                    if last_sep != -1:
                        end = last_sep + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            # 跳过太小的块（除了最后一个）
            if len(chunk_text) >= self.min_chunk_size or start + self.chunk_size >= len(text):
                if chunk_text:
                    chunk = Chunk(
                        document_id=document_id or "",
                        content=chunk_text,
                        chunk_index=chunk_index,
                        start_char=start,
                        end_char=end,
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            # 移动起始位置（考虑重叠）
            start = end - self.overlap if end < len(text) else end
            
            # 避免死循环
            if start >= end:
                start = end
        
        logger.debug(f"固定字符切片: 文本长度 {len(text)}, 生成 {len(chunks)} 个块")
        return chunks
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        return (
            self.chunk_size > 0
            and self.overlap >= 0
            and self.overlap < self.chunk_size
            and self.min_chunk_size > 0
        )


__all__ = ["FixedCharsChunker", "FixedCharsChunkerConfig"]
