"""Reranker 客户端"""
import httpx
from typing import List, Optional, Tuple

from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class RerankerClient:
    """Reranker API 客户端"""
    
    def __init__(
        self,
        api_type: str = "local",
        api_url: str = "http://localhost:8002/v1/rerank",
        api_key: str = "",
        model: str = "qwen3-reranker-0.6b",
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
                base_url=self.api_url.rstrip("/v1/rerank").rstrip("/"),
                headers=headers,
                timeout=60.0,
            )
        return self._client
    
    async def close(self) -> None:
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: int = None,
    ) -> List[Tuple[int, float]]:
        """重排文档
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_n: 返回数量
            
        Returns:
            [(文档索引, 分数)] 列表
        """
        if not documents:
            return []
        
        try:
            client = self._get_client()
            
            response = await client.post(
                "/v1/rerank",
                json={
                    "model": self.model,
                    "query": query,
                    "documents": documents,
                    "top_n": top_n or len(documents),
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append((item["index"], item["relevance_score"]))
            
            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"Reranker 请求失败: {e}")
            return [(i, 1.0 / (i + 1)) for i in range(len(documents))]
        except Exception as e:
            logger.error(f"Reranker 调用失败: {e}")
            return [(i, 1.0 / (i + 1)) for i in range(len(documents))]


__all__ = ["RerankerClient"]
