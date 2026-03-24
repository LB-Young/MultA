"""CLI 命令"""
import asyncio
import click
from pathlib import Path

from src.infrastructure.config import get_config
from src.infrastructure.logging.setup import setup_logging, get_logger
from src.infrastructure.storage.file_storage import FileStorage
from src.infrastructure.extractors import ExtractorFactory
from src.infrastructure.chunkers import ChunkerFactory
from src.infrastructure.vector_db import VectorStoreFactory
from src.infrastructure.embedding import EmbeddingClient
from src.infrastructure.storage.file_storage import InMemoryDocumentRepository
from src.application.services import DocumentService, ChunkService

setup_logging()
logger = get_logger(__name__)


@click.group()
def cli():
    """FileSystem RAG 命令行工具"""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--chunk-size", default=500, help="块大小")
@click.option("--overlap", default=50, help="重叠大小")
@click.option("--strategy", default="fixed_chars", help="切片策略")
def process(file_path: str, chunk_size: int, overlap: int, strategy: str):
    """处理单个文件"""
    async def _process():
        config = get_config()
        config.load()
        
        # 初始化组件
        storage = FileStorage(upload_dir="data/uploads")
        repo = InMemoryDocumentRepository()
        doc_service = DocumentService(storage, repo)
        embedding = EmbeddingClient()
        
        chunk_service = ChunkService(doc_service, embedding)
        
        # 初始化向量数据库
        VectorStoreFactory.initialize({
            "type": config.settings.vector_db.type,
            "host": config.settings.vector_db.host,
            "port": config.settings.vector_db.port,
            "collection_name": config.settings.vector_db.collection_name,
        })
        
        # 上传文件
        with open(file_path, "rb") as f:
            content = f.read()
        
        filename = Path(file_path).name
        document = await doc_service.upload_document(content, filename)
        
        click.echo(f"文件已上传: {document.id}")
        
        # 处理文档
        chunks, vectors = await chunk_service.process_document(
            document_id=document.id,
            chunk_size=chunk_size,
            overlap=overlap,
            strategy=strategy,
        )
        
        # 存储
        await chunk_service.store_chunks(document.id, chunks, vectors)
        
        click.echo(f"处理完成！生成 {len(chunks)} 个切片")
    
    asyncio.run(_process())


@cli.command()
def init():
    """初始化数据目录"""
    dirs = [
        "data/uploads",
        "data/processed",
        "logs",
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        click.echo(f"创建目录: {d}")
    
    click.echo("初始化完成！")


@cli.command()
def info():
    """显示系统信息"""
    config = get_config()
    config.load()
    
    click.echo("=== FileSystem RAG 系统信息 ===")
    click.echo(f"向量数据库: {config.settings.vector_db.type}")
    click.echo(f"集合名称: {config.settings.vector_db.collection_name}")
    click.echo(f"LLM URL: {config.settings.api.llm.url}")
    click.echo(f"Embedding URL: {config.settings.api.embedding.url}")


@cli.command()
@click.argument("collection_name")
@click.option("--recreate", is_flag=True, help="删除并重新创建")
def collection(collection_name: str, recreate: bool):
    """管理向量集合"""
    async def _collection():
        config = get_config()
        config.load()
        
        VectorStoreFactory.initialize({
            "type": config.settings.vector_db.type,
            "host": config.settings.vector_db.host,
            "port": config.settings.vector_db.port,
            "collection_name": collection_name,
            "vector_size": config.settings.vector_db.vector_size,
        })
        
        store = VectorStoreFactory.get_store(collection_name)
        await store.initialize()
        
        if recreate:
            if await store.collection_exists(collection_name):
                await store.delete_collection(collection_name)
                click.echo(f"已删除集合: {collection_name}")
            
            await store.create_collection(
                collection_name,
                config.settings.vector_db.vector_size,
            )
            click.echo(f"已创建集合: {collection_name}")
        else:
            if await store.collection_exists(collection_name):
                info = await store.get_collection_info(collection_name)
                click.echo(f"集合已存在: {collection_name}")
                click.echo(f"  向量数量: {info.get('vectors_count', 0)}")
                click.echo(f"  状态: {info.get('status', 'unknown')}")
            else:
                click.echo(f"集合不存在: {collection_name}")


if __name__ == "__main__":
    cli()
