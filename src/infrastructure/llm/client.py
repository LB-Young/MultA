"""LLM 客户端"""
import httpx
from typing import List, Optional, Dict, Any

from src.infrastructure.logging.setup import get_logger
from src.infrastructure.exceptions import LLMError

logger = get_logger(__name__)


class LLMClient:
    """LLM API 客户端"""
    
    def __init__(
        self,
        api_type: str = "local",
        api_url: str = "http://localhost:11434/api/chat",
        api_key: str = "",
        model: str = "qwen2.5",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ):
        self.api_type = api_type
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self._client = httpx.AsyncClient(
                base_url=self.api_url.rstrip("/api/chat").rstrip("/"),
                headers=headers,
                timeout=120.0,
            )
        return self._client
    
    async def close(self) -> None:
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        **kwargs,
    ) -> str:
        """发送对话请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            **kwargs: 其他参数
            
        Returns:
            助手回复
        """
        try:
            client = self._get_client()
            
            # 构建消息
            full_messages = []
            
            # 系统提示词
            if system_prompt:
                full_messages.append({
                    "role": "system",
                    "content": system_prompt,
                })
            
            full_messages.extend(messages)
            
            if self.api_type == "local":
                # Ollama API
                response = await client.post(
                    "/api/chat",
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get("temperature", self.temperature),
                            "num_predict": kwargs.get("max_tokens", self.max_tokens),
                        },
                    },
                )
            else:
                # OpenAI 兼容 API
                response = await client.post(
                    "/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "temperature": kwargs.get("temperature", self.temperature),
                        "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    },
                )
            
            response.raise_for_status()
            data = response.json()
            
            if "message" in data:
                # Ollama 格式
                return data["message"]["content"]
            elif "choices" in data:
                # OpenAI 格式
                return data["choices"][0]["message"]["content"]
            else:
                raise LLMError(f"未知的响应格式: {data}")
                
        except httpx.HTTPError as e:
            logger.error(f"LLM 请求失败: {e}")
            raise LLMError(f"API 请求失败: {e}")
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise LLMError(f"调用失败: {e}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs,
    ) -> str:
        """生成文本（单轮对话）
        
        Args:
            prompt: 输入提示
            system_prompt: 系统提示词
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, system_prompt, **kwargs)


class OllamaClient(LLMClient):
    """Ollama LLM 客户端"""
    
    def __init__(self, model: str = "qwen2.5"):
        super().__init__(
            api_type="local",
            api_url="http://localhost:11434",
            model=model,
        )


__all__ = ["LLMClient", "OllamaClient"]
