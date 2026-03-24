"""pytest 配置"""
import sys
from pathlib import Path

# 添加 src 到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.fixture
def sample_text():
    """示例文本"""
    return """这是第一段文本。
这是一个较长的段落，包含多个句子。

这是第二段文本。
也包含多个句子。

这是第三段文本。
用于测试切片功能。"""


@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "api": {
            "embedding": {
                "type": "local",
                "url": "http://localhost:8001/embed",
                "key": "",
                "model": "",
            },
            "llm": {
                "type": "local",
                "url": "http://localhost:11434/api/chat",
                "key": "",
                "model": "qwen2.5",
                "max_tokens": 2048,
                "temperature": 0.7,
            },
        },
        "vector_db": {
            "type": "chroma",
            "persist_directory": "./test_chroma_db",
            "collection_name": "test_knowledge_base",
            "vector_size": 1536,
            "distance": "Cosine",
        },
        "chunking": {
            "strategy": "fixed_chars",
            "chunk_size": 100,
            "overlap": 20,
        },
    }
