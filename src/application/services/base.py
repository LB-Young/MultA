"""应用服务基类"""
from typing import Optional

from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class BaseService:
    """应用服务基类
    
    提供基础的服务功能，包括日志、配置等
    """
    
    def __init__(self):
        self.logger = logger.bind(service=self.__class__.__name__)
    
    async def initialize(self) -> None:
        """初始化服务"""
        pass
    
    async def cleanup(self) -> None:
        """清理服务资源"""
        pass


__all__ = ["BaseService"]
