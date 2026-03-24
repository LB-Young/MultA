"""FastAPI 主应用"""
import uuid
from contextvars import ContextVar
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.infrastructure.logging.setup import setup_logging, LogContext, trace_id_var, get_logger
from src.infrastructure.config import get_config, get_settings
from src.infrastructure.exceptions import FileSystemError
from src.api.routers import (
    health_router,
    documents_router,
    chunks_router,
    rag_router,
    agent_router,
)
from src.api.deps import init_vector_store
from src.api.routers.health import RUNTIME_CONFIG

# 设置日志
setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="FileSystem RAG API",
        description="企业知识库 RAG 系统 API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # ==================== 中间件 ====================
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        # 生成 trace_id
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
        token = trace_id_var.set(trace_id)
        
        start_time = datetime.now()
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 记录日志
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"{request.method} {request.url.path} "
                f"- {response.status_code} ({duration:.3f}s) "
                f"[{trace_id}]"
            )
            
            # 添加 trace_id 到响应头
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        finally:
            trace_id_var.reset(token)
    
    # ==================== 异常处理 ====================
    
    @app.exception_handler(FileSystemError)
    async def filesystem_error_handler(request: Request, exc: FileSystemError):
        """处理自定义异常"""
        return JSONResponse(
            status_code=400,
            content=exc.to_dict(),
            headers={"X-Trace-ID": trace_id_var.get() or ""},
        )
    
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        """处理通用异常"""
        logger.error(f"未处理的异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                    "details": {"trace": str(exc)} if request.app.debug else {},
                }
            },
            headers={"X-Trace-ID": trace_id_var.get() or ""},
        )
    
    # ==================== 路由 ====================
    
    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(chunks_router)
    app.include_router(rag_router)
    app.include_router(agent_router)
    
    # ==================== 生命周期 ====================
    
    @app.on_event("startup")
    async def startup_event():
        """启动时初始化"""
        logger.info("正在启动 FileSystem RAG API...")
        
        # 加载配置
        config = get_config()
        config.load()
        settings = get_settings()
        
        logger.info(f"配置已加载: {settings.vector_db.type}")

        # 将 settings.yaml 的值同步到 RUNTIME_CONFIG（让依赖注入使用正确地址）
        RUNTIME_CONFIG["llm_url"] = settings.api.llm.url
        RUNTIME_CONFIG["llm_model"] = settings.api.llm.model
        RUNTIME_CONFIG["llm_type"] = settings.api.llm.type
        RUNTIME_CONFIG["embedding_url"] = settings.api.embedding.url
        RUNTIME_CONFIG["embedding_model"] = settings.api.embedding.model
        RUNTIME_CONFIG["embedding_type"] = settings.api.embedding.type
        RUNTIME_CONFIG["reranker_url"] = settings.api.reranker.url
        RUNTIME_CONFIG["reranker_enabled"] = settings.api.reranker.enabled

        logger.info(
            f"运行时配置: embedding={settings.api.embedding.url}/{settings.api.embedding.model}, "
            f"llm={settings.api.llm.url}/{settings.api.llm.model}"
        )

        # 初始化向量数据库
        try:
            await init_vector_store()
            logger.info("向量数据库初始化完成")
        except Exception as e:
            logger.warning(f"向量数据库初始化失败: {e}")
        
        logger.info("FileSystem RAG API 启动完成")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """关闭时清理"""
        logger.info("正在关闭 FileSystem RAG API...")
        
        # TODO: 清理资源
        
        logger.info("FileSystem RAG API 已关闭")
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
