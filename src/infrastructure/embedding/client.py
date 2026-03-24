"""Embedding 客户端"""
import httpx
from typing import List, Optional

from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import EmbeddingFailedError

logger = get_logger(__name__)


class EmbeddingClient:
    """Embedding API 客户端"""
    
    def __init__(
        self,
        api_type: str = "local",
        api_url: str = "http://localhost:8001/embed",
        api_key: str = "",
        model: str = "",
    ):
        self.api_type = api_type
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self._client = httpx.AsyncClient(
                base_url=self.api_url.rstrip("/"),
                headers=headers,
                timeout=60.0,
            )
        return self._client
    
    async def close(self) -> None:
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def embed(self, text: str) -> List[float]:
        """生成单条文本的 embedding
        
        Args:
            text: 输入文本
            
        Returns:
            embedding 向量
        """
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成 embedding

        Args:
            texts: 输入文本列表

        Returns:
            embedding 向量列表
        """
        if not texts:
            return []

        try:
            client = self._get_client()
            model = self.model or "nomic-embed-text"

            if self.api_type == "local":
                # Ollama API - 使用 /api/embeddings 和 prompt 参数
                results = []
                for text in texts:
                    response = await client.post(
                        "/api/embeddings",
                        json={
                            "model": model,
                            "prompt": text,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    if "embedding" in data:
                        results.append(data["embedding"])
                    elif "embeddings" in data:
                        results.extend(data["embeddings"])
                return results
            else:
                # OpenAI 兼容 API - 使用 /v1/embeddings 和 input 参数
                response = await client.post(
                    "/v1/embeddings",
                    json={
                        "model": model,
                        "input": texts,
                    },
                )

                response.raise_for_status()
                data = response.json()

                if "data" in data:
                    # OpenAI 格式
                    embeddings = sorted(data["data"], key=lambda x: x["index"])
                    return [item["embedding"] for item in embeddings]
                elif "embeddings" in data:
                    # Ollama 兼容格式
                    return data["embeddings"]
                else:
                    raise EmbeddingFailedError(f"未知的响应格式: {data}")

        except httpx.HTTPError as e:
            logger.error(f"Embedding 请求失败: {e}")
            raise EmbeddingFailedError(f"API 请求失败: {e}")
        except Exception as e:
            logger.error(f"Embedding 生成失败: {e}")
            raise EmbeddingFailedError(f"生成失败: {e}")
    
    async def get_dimension(self) -> int:
        """获取 embedding 维度"""
        try:
            test_embedding = await self.embed("test")
            return len(test_embedding)
        except Exception as e:
            logger.warning(f"无法获取 embedding 维度: {e}")
            return 1536  # 默认维度


class LocalEmbeddingClient(EmbeddingClient):
    """本地 Embedding 客户端"""
    
    def __init__(self, model: str = "nomic-embed-text"):
        super().__init__(
            api_type="local",
            api_url="http://localhost:8001",
            model=model,
        )


__all__ = ["EmbeddingClient", "LocalEmbeddingClient"]
