"""固定 Token 数切片器"""
from typing import List, Optional

from src.domain.entities.chunk import Chunk
from src.domain.plugins import ChunkerConfig
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class FixedTokensChunkerConfig(ChunkerConfig):
    """固定 Token 切片器配置"""
    name: str = "fixed_tokens"
    chunk_size: int = 500  # token 数
    overlap: int = 50
    min_chunk_size: int = 50


class FixedTokensChunker:
    """固定 Token 数切片器
    
    使用 tokenizer 将文本转换为 token，然后按固定 token 数切分
    """
    
    name = "fixed_tokens"
    
    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        min_chunk_size: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        self.encoding_name = encoding_name
        self._encoding = None
    
    def _get_encoding(self):
        """获取 tokenizer（延迟加载）"""
        if self._encoding is None:
            try:
                import tiktoken
                self._encoding = tiktoken.get_encoding(self.encoding_name)
            except ImportError:
                logger.warning("tiktoken 未安装，使用字符估算")
                self._encoding = None
        return self._encoding
    
    def _count_tokens(self, text: str) -> int:
        """计算 token 数量"""
        encoding = self._get_encoding()
        if encoding:
            return len(encoding.encode(text))
        else:
            # 粗略估算：中文约 2 字符/token，英文约 4 字符/token
            chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
            other_chars = len(text) - chinese_chars
            return int(chinese_chars / 2 + other_chars / 4)
    
    def chunk(self, text: str, document_id: str = None, **kwargs) -> List[Chunk]:
        """将文本切分为固定 token 数的块
        
        Args:
            text: 输入文本
            document_id: 文档 ID
            
        Returns:
            切片列表
        """
        if not text or not text.strip():
            return []
        
        encoding = self._get_encoding()
        
        if encoding is None:
            # 如果没有 tokenizer，使用固定字符切片
            from .fixed_chars import FixedCharsChunker
            fallback = FixedCharsChunker(
                chunk_size=self.chunk_size * 3,  # 粗略估算
                overlap=self.overlap * 3,
                min_chunk_size=self.min_chunk_size * 3,
            )
            return fallback.chunk(text, document_id, **kwargs)
        
        # 编码文本
        tokens = encoding.encode(text)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            
            # 解码回文本
            chunk_tokens = tokens[start:end]
            chunk_text = encoding.decode(chunk_tokens)
            
            if chunk_text.strip():
                # 计算字符位置
                start_char = len(encoding.decode(tokens[:start])) if start > 0 else 0
                end_char = start_char + len(chunk_text)
                
                chunk = Chunk(
                    document_id=document_id or "",
                    content=chunk_text.strip(),
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=end_char,
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # 移动起始位置
            start = end - self.overlap if end < len(tokens) else end
        
        logger.debug(f"固定 Token 切片: 文本长度 {len(text)}, token 数 {len(tokens)}, 生成 {len(chunks)} 个块")
        return chunks
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        return (
            self.chunk_size > 0
            and self.overlap >= 0
            and self.overlap < self.chunk_size
        )


__all__ = ["FixedTokensChunker", "FixedTokensChunkerConfig"]
