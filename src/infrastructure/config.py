"""配置管理"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class EmbeddingConfig(BaseModel):
    """Embedding 配置"""
    type: str = "local"
    url: str = "http://localhost:8001/embed"
    key: str = ""
    model: str = ""


class LLMConfig(BaseModel):
    """LLM 配置"""
    type: str = "local"
    url: str = "http://localhost:11434/api/chat"
    key: str = ""
    model: str = "qwen2.5"
    max_tokens: int = 2048
    temperature: float = 0.7


class RerankerConfig(BaseModel):
    """Reranker 配置"""
    type: str = "local"
    url: str = "http://localhost:8002/v1/rerank"
    key: str = ""
    model: str = "qwen3-reranker-0.6b"
    enabled: bool = False


class APIConfig(BaseModel):
    """API 配置"""
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)


class ExtractorExternalConfig(BaseModel):
    """外部提取器 API 配置"""
    enabled: bool = False
    url: str = ""
    key: str = ""


class ExtractorsConfig(BaseModel):
    """文件提取配置"""
    builtin: list[str] = ["txt", "md", "json", "docx", "xlsx", "pptx", "pdf"]
    external: dict[str, ExtractorExternalConfig] = Field(default_factory=dict)


class ChunkingConfig(BaseModel):
    """切片配置"""
    strategy: str = "fixed_chars"
    chunk_size: int = 500
    overlap: int = 50
    min_chunk_size: int = 50


class VectorDBConfig(BaseModel):
    """向量数据库配置"""
    type: str = "qdrant"
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "knowledge_base"
    vector_size: int = 1536
    distance: str = "Cosine"


class RAGConfig(BaseModel):
    """RAG 配置"""
    top_k: int = 5
    rerank_top_k: int = 10
    min_score: float = 0.5


class StorageConfig(BaseModel):
    """存储配置"""
    upload_dir: Path = Path("data/uploads")
    processed_dir: Path = Path("data/processed")
    max_file_size: int = 52428800  # 50MB


class Settings(BaseModel):
    """应用配置"""
    api: APIConfig = Field(default_factory=APIConfig)
    extractors: ExtractorsConfig = Field(default_factory=ExtractorsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)


class ConfigManager:
    """配置管理器"""
    
    _instance: Optional["ConfigManager"] = None
    _settings: Optional[Settings] = None
    
    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._config_path: Optional[Path] = None
    
    def load(self, config_path: Optional[str | Path] = None) -> Settings:
        """加载配置
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
            
        Returns:
            配置对象
        """
        if config_path is None:
            # 默认路径：config/settings.yaml
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            # 如果配置文件不存在，使用默认配置
            self._settings = Settings()
            return self._settings
        
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}
        
        self._settings = Settings(**config_data)
        self._config_path = config_path
        
        return self._settings
    
    @property
    def settings(self) -> Settings:
        """获取配置对象"""
        if self._settings is None:
            self.load()
        return self._settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键，支持点号分隔，如 "api.llm.url"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split(".")
        value = self.settings.model_dump()
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        
        return value
    
    def reload(self) -> Settings:
        """重新加载配置"""
        return self.load(self._config_path)
    
    def update(self, updates: dict[str, Any]) -> Settings:
        """更新配置
        
        Args:
            updates: 配置更新
            
        Returns:
            更新后的配置
        """
        current = self.settings.model_dump()
        
        def deep_update(base: dict, updates: dict) -> dict:
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    base[key] = deep_update(base[key], value)
                else:
                    base[key] = value
            return base
        
        merged = deep_update(current, updates)
        self._settings = Settings(**merged)
        return self._settings


@lru_cache()
def get_config() -> ConfigManager:
    """获取配置管理器单例"""
    return ConfigManager()


def get_settings() -> Settings:
    """获取配置对象"""
    return get_config().settings


__all__ = [
    "Settings",
    "ConfigManager",
    "get_config",
    "get_settings",
    "EmbeddingConfig",
    "LLMConfig",
    "RerankerConfig",
    "APIConfig",
    "ExtractorsConfig",
    "ChunkingConfig",
    "VectorDBConfig",
    "RAGConfig",
    "StorageConfig",
]
