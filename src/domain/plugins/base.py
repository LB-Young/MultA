"""插件基类和注册中心"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Type, Callable, Dict

from pydantic import BaseModel


T = TypeVar("T")


class PluginConfig(BaseModel):
    """插件配置基类"""
    name: str
    enabled: bool = True


class PluginRegistry:
    """插件注册中心
    
    用法:
        @PluginRegistry.register("extractor")
        class MyExtractor:
            ...
    
    获取插件:
        extractor = PluginRegistry.get("extractor", "my_extractor")
    """
    
    _plugins: Dict[str, Dict[str, Type[PluginConfig]]] = {
        "extractor": {},
        "chunker": {},
        "retriever": {},
        "embedding": {},
        "llm": {},
        "reranker": {},
    }
    
    _instances: Dict[str, Dict[str, Any]] = {
        "extractor": {},
        "chunker": {},
        "retriever": {},
        "embedding": {},
        "llm": {},
        "reranker": {},
    }
    
    @classmethod
    def register(
        cls, 
        plugin_type: str, 
        name: str = None,
        singleton: bool = True,
    ) -> Callable[[Type[PluginConfig]], Type[PluginConfig]]:
        """注册插件
        
        Args:
            plugin_type: 插件类型
            name: 插件名称，默认使用类名小写
            singleton: 是否单例
            
        Returns:
            装饰器函数
        """
        def decorator(plugin_class: Type[PluginConfig]) -> Type[PluginConfig]:
            plugin_name = name or plugin_class.__name__.lower()
            
            if plugin_type not in cls._plugins:
                cls._plugins[plugin_type] = {}
            
            cls._plugins[plugin_type][plugin_name] = plugin_class
            
            return plugin_class
        
        return decorator
    
    @classmethod
    def get(cls, plugin_type: str, name: str, **kwargs) -> Any:
        """获取插件实例
        
        Args:
            plugin_type: 插件类型
            name: 插件名称
            **kwargs: 插件构造参数
            
        Returns:
            插件实例
            
        Raises:
            PluginNotFoundError: 插件不存在
        """
        from src.infrastructure.exceptions import PluginNotFoundError
        
        if plugin_type not in cls._plugins:
            raise PluginNotFoundError(plugin_type, name)
        
        if name not in cls._plugins[plugin_type]:
            available = list(cls._plugins[plugin_type].keys())
            raise PluginNotFoundError(plugin_type, name)
        
        # 检查是否有单例实例
        if plugin_type in cls._instances and name in cls._instances[plugin_type]:
            return cls._instances[plugin_type][name]
        
        # 创建新实例
        plugin_class = cls._plugins[plugin_type][name]
        instance = plugin_class(**kwargs)
        
        # 缓存单例
        if plugin_type not in cls._instances:
            cls._instances[plugin_type] = {}
        cls._instances[plugin_type][name] = instance
        
        return instance
    
    @classmethod
    def list_plugins(cls, plugin_type: str) -> list[str]:
        """列出指定类型的所有插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            插件名称列表
        """
        if plugin_type not in cls._plugins:
            return []
        return list(cls._plugins[plugin_type].keys())
    
    @classmethod
    def list_all_plugins(cls) -> dict[str, list[str]]:
        """列出所有插件
        
        Returns:
            {plugin_type: [plugin_names]}
        """
        return {pt: list(plugins.keys()) for pt, plugins in cls._plugins.items()}
    
    @classmethod
    def unregister(cls, plugin_type: str, name: str) -> bool:
        """取消注册插件
        
        Args:
            plugin_type: 插件类型
            name: 插件名称
            
        Returns:
            是否成功取消
        """
        if plugin_type in cls._plugins and name in cls._plugins[plugin_type]:
            del cls._plugins[plugin_type][name]
            
            # 清除实例
            if plugin_type in cls._instances and name in cls._instances[plugin_type]:
                del cls._instances[plugin_type][name]
            
            return True
        return False
    
    @classmethod
    def clear(cls) -> None:
        """清除所有插件注册"""
        cls._plugins = {k: {} for k in cls._plugins}
        cls._instances = {k: {} for k in cls._instances}


class PluginBase(ABC, Generic[T]):
    """插件基类
    
    提供插件的基础功能，包括配置、初始化、验证等
    """
    
    config: T
    
    def __init__(self, config: T = None, **kwargs):
        """初始化插件
        
        Args:
            config: 插件配置
            **kwargs: 其他配置参数
        """
        if config is not None:
            self.config = config
        else:
            self.config = self._create_default_config(**kwargs)
    
    @abstractmethod
    def _create_default_config(self, **kwargs) -> T:
        """创建默认配置
        
        Returns:
            插件配置对象
        """
        ...
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化插件
        
        在插件被首次使用时调用，用于加载资源、建立连接等
        """
        ...
    
    @abstractmethod
    async def validate(self) -> bool:
        """验证插件是否可用
        
        Returns:
            是否可用
        """
        ...
    
    async def cleanup(self) -> None:
        """清理插件资源
        
        在插件不再使用时调用，用于释放资源、关闭连接等
        """
        pass


__all__ = [
    "PluginConfig",
    "PluginRegistry",
    "PluginBase",
]
