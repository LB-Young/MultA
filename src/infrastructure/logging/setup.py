"""结构化日志配置"""
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel

# 请求级别 trace_id
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:
    """获取当前请求的 trace_id"""
    return trace_id_var.get()


def generate_trace_id() -> str:
    """生成新的 trace_id"""
    return str(uuid.uuid4())[:8]


class LogConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    file_path: Path = Path("logs/app.log")
    error_file_path: Path = Path("logs/error.log")
    rotation: str = "10 MB"
    retention: str = "7 days"
    compression: str = "zip"
    enable_console: bool = True
    enable_file: bool = True


def setup_logging(config: Optional[LogConfig] = None) -> None:
    """配置日志系统

    Args:
        config: 日志配置，如果不提供则使用默认配置
    """
    if config is None:
        config = LogConfig()

    # 移除默认的 handler
    logger.remove()

    # 配置格式（包含 trace_id，safe 处理 None）
    def safe_trace_id(record):
        trace_id = record["extra"].get("trace_id")
        return str(trace_id)[:8] if trace_id else "--------"

    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # 控制台输出
    if config.enable_console:
        logger.add(
            sys.stdout,
            level=config.level,
            format=log_format,
            colorize=True,
            enqueue=False,  # 同步输出，避免多进程问题
        )

    # 文件输出
    if config.enable_file:
        # 确保日志目录存在
        config.file_path.parent.mkdir(parents=True, exist_ok=True)
        config.error_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 普通日志
        logger.add(
            config.file_path,
            level="DEBUG",
            format=log_format,
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            enqueue=False,
            serialize=False,
        )

        # 错误日志单独记录
        logger.add(
            config.error_file_path,
            level="ERROR",
            format=log_format,
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            enqueue=False,
            serialize=False,
        )


def get_logger(name: str) -> "logger":
    """获取带 trace_id 的 logger
    
    Args:
        name: logger 名称，通常使用 __name__
        
    Returns:
        配置好的 logger 实例
    """
    return logger.bind(name=name, trace_id=get_trace_id())


class LogContext:
    """日志上下文管理器，用于设置 trace_id"""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or generate_trace_id()
        self.token: Optional[object] = None
    
    def __enter__(self) -> str:
        self.token = trace_id_var.set(self.trace_id)
        return self.trace_id
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.token is not None:
            trace_id_var.reset(self.token)


__all__ = [
    "setup_logging",
    "get_logger",
    "get_trace_id",
    "generate_trace_id",
    "LogContext",
    "LogConfig",
    "trace_id_var",
]
