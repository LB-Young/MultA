"""文件存储服务"""
import json
import shutil
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO

from src.domain.entities.document import Document, DocumentType, DocumentStatus
from src.domain.repositories.document_repo import DocumentRepository
from src.infrastructure.exceptions import (
    DocumentNotFoundError,
    FileReadError,
    UnsupportedFileTypeError,
    FileTooLargeError,
)
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class FileStorage:
    """文件存储服务"""
    
    # 文件类型映射
    EXTENSION_TO_TYPE = {
        ".txt": DocumentType.TEXT,
        ".md": DocumentType.MARKDOWN,
        ".json": DocumentType.TEXT,
        ".docx": DocumentType.WORD,
        ".doc": DocumentType.WORD,
        ".xlsx": DocumentType.EXCEL,
        ".xls": DocumentType.EXCEL,
        ".pptx": DocumentType.OTHER,
        ".ppt": DocumentType.OTHER,
        ".pdf": DocumentType.PDF,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".png": DocumentType.IMAGE,
        ".gif": DocumentType.IMAGE,
        ".bmp": DocumentType.IMAGE,
        ".mp3": DocumentType.AUDIO,
        ".wav": DocumentType.AUDIO,
        ".m4a": DocumentType.AUDIO,
    }
    
    MIME_TYPES = {
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".json": "application/json",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
    }
    
    def __init__(
        self,
        upload_dir: Path | str,
        max_file_size: int = 52428800,  # 50MB
    ):
        self.upload_dir = Path(upload_dir)
        self.max_file_size = max_file_size
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_type(self, extension: str) -> DocumentType:
        """获取文件类型"""
        doc_type = self.EXTENSION_TO_TYPE.get(extension.lower())
        if doc_type is None:
            return DocumentType.OTHER
        return doc_type
    
    def _get_mime_type(self, extension: str) -> str:
        """获取 MIME 类型"""
        return self.MIME_TYPES.get(extension.lower(), "application/octet-stream")
    
    async def save_file(
        self,
        file_content: bytes,
        filename: str,
    ) -> Document:
        """保存上传的文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            
        Returns:
            文档实体
        """
        extension = Path(filename).suffix.lower()
        
        # 检查文件类型
        if extension not in self.EXTENSION_TO_TYPE:
            raise UnsupportedFileTypeError(extension)
        
        # 检查文件大小
        file_size = len(file_content)
        if file_size > self.max_file_size:
            raise FileTooLargeError(filename, file_size, self.max_file_size)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = self.upload_dir / unique_filename
        
        # 保存文件
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        logger.info(f"文件已保存: {file_path}")
        
        # 创建文档实体
        document = Document(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=self._get_file_type(extension),
            mime_type=self._get_mime_type(extension),
            extension=extension,
            status=DocumentStatus.UPLOADED,
        )
        
        return document
    
    async def read_file(self, file_path: Path) -> str:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        if not file_path.exists():
            raise FileReadError(str(file_path), "文件不存在")
        
        try:
            # 根据文件类型选择读取方式
            extension = file_path.suffix.lower()
            
            if extension in [".txt", ".md", ".json"]:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    return await f.read()
            else:
                # 二进制文件需要用提取器处理
                async with aiofiles.open(file_path, "rb") as f:
                    content = await f.read()
                    return content.decode("utf-8", errors="ignore")
                    
        except Exception as e:
            raise FileReadError(str(file_path), str(e))
    
    async def delete_file(self, file_path: Path) -> bool:
        """删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件已删除: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {file_path} - {e}")
            return False
    
    def file_exists(self, file_path: Path) -> bool:
        """检查文件是否存在"""
        return file_path.exists()


class JSONDocumentRepository(DocumentRepository):
    """JSON 文件文档仓储（持久化存储）"""

    def __init__(self, storage_path: str = "data/documents.json"):
        self._storage_path = Path(storage_path)
        self._documents: dict[str, Document] = {}
        self._load()

    def _load(self) -> None:
        """从文件加载数据"""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for doc_data in data:
                        doc_data["file_path"] = Path(doc_data["file_path"])
                        self._documents[doc_data["id"]] = Document(**doc_data)
                logger.info(f"已加载 {len(self._documents)} 个文档")
            except Exception as e:
                logger.warning(f"加载文档数据失败: {e}")

    def _save(self) -> None:
        """保存数据到文件"""
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = []
            for doc in self._documents.values():
                doc_dict = doc.model_dump()
                doc_dict["file_path"] = str(doc_dict["file_path"])
                doc_dict["file_type"] = doc_dict["file_type"].value
                doc_dict["status"] = doc_dict["status"].value
                data.append(doc_dict)
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存文档数据失败: {e}")

    async def save(self, document: Document) -> Document:
        self._documents[document.id] = document
        self._save()
        return document

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
    ) -> list[Document]:
        docs = list(self._documents.values())

        if status:
            docs = [d for d in docs if d.status.value == status]

        # 按创建时间倒序
        docs.sort(key=lambda d: d.created_at, reverse=True)

        return docs[skip:skip + limit]

    async def delete(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            self._save()
            return True
        return False

    async def update(self, document: Document) -> Document:
        self._documents[document.id] = document
        self._save()
        return document

    async def count(self, status: str = None) -> int:
        if status:
            return sum(1 for d in self._documents.values() if d.status.value == status)
        return len(self._documents)


class InMemoryDocumentRepository(DocumentRepository):
    """内存文档仓储（开发/测试用）"""

    def __init__(self):
        self._documents: dict[str, Document] = {}

    async def save(self, document: Document) -> Document:
        self._documents[document.id] = document
        return document

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
    ) -> list[Document]:
        docs = list(self._documents.values())

        if status:
            docs = [d for d in docs if d.status.value == status]

        # 按创建时间倒序
        docs.sort(key=lambda d: d.created_at, reverse=True)

        return docs[skip:skip + limit]

    async def delete(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    async def update(self, document: Document) -> Document:
        self._documents[document.id] = document
        return document

    async def count(self, status: str = None) -> int:
        if status:
            return sum(1 for d in self._documents.values() if d.status.value == status)
        return len(self._documents)


__all__ = [
    "FileStorage",
    "InMemoryDocumentRepository",
    "JSONDocumentRepository",
]
