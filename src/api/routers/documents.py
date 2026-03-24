"""文档管理路由"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.application.services import DocumentService, ChunkService
from src.application.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
)
from src.api.deps import (
    get_document_service,
    get_chunk_service,
)
from src.infrastructure.logging.setup import get_logger, LogContext

router = APIRouter(prefix="/documents", tags=["文档管理"])
logger = get_logger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
):
    """上传文档"""
    with LogContext() as trace:
        try:
            # 读取文件内容
            content = await file.read()
            
            # 保存文档
            document = await document_service.upload_document(
                file_content=content,
                filename=file.filename,
            )
            
            return DocumentUploadResponse(
                id=document.id,
                filename=document.filename,
                original_filename=document.original_filename,
                file_size=document.file_size,
                file_type=document.file_type.value,
                status=document.status.value,
            )
            
        except Exception as e:
            logger.error(f"上传文档失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    document_service: DocumentService = Depends(get_document_service),
):
    """列出文档"""
    try:
        documents = await document_service.list_documents(skip, limit, status)
        
        return DocumentListResponse(
            items=[document_service.to_response(d).model_dump() for d in documents],
            total=len(documents),
            skip=skip,
            limit=limit,
        )
        
    except Exception as e:
        logger.error(f"列出文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
):
    """获取文档详情"""
    try:
        document = await document_service.get_document(document_id)
        return document_service.to_response(document).model_dump()
        
    except Exception as e:
        logger.error(f"获取文档失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """删除文档"""
    try:
        await document_service.delete_document(document_id)
        return {"message": "文档删除成功", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: str,
    request: DocumentProcessRequest = None,
    document_service: DocumentService = Depends(get_document_service),
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """处理文档（提取文本、切片、向量化）"""
    if request is None:
        request = DocumentProcessRequest()
    
    with LogContext() as trace:
        try:
            # 处理文档
            chunks, vectors = await chunk_service.process_document(
                document_id=document_id,
                chunk_size=request.chunk_size,
                overlap=request.overlap,
                strategy=request.strategy,
            )

            # 存储切片
            await chunk_service.store_chunks(document_id, chunks, vectors)

            # 保存文档元数据到仓储
            await document_service.update_metadata(
                document_id,
                text_length=sum(c.length for c in chunks),
                chunk_count=len(chunks),
            )

            # 重新获取完整文档（包含 text_length 从提取步骤）
            document = await document_service.get_document(document_id)

            return DocumentProcessResponse(
                id=document.id,
                status=document.status.value,
                text_length=document.text_length,
                chunk_count=document.chunk_count,
            )
            
        except Exception as e:
            logger.error(f"处理文档失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))


SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".docx", ".pdf", ".xlsx", ".pptx"}


class FolderUploadRequest(BaseModel):
    folder_path: str
    process_immediately: bool = True
    dry_run: bool = False  # 预览模式：只扫描不保存
    chunk_size: int = 500
    overlap: int = 50
    strategy: str = "fixed_chars"


@router.post("/upload-folder")
async def upload_folder(
    request: FolderUploadRequest,
    document_service: DocumentService = Depends(get_document_service),
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """扫描文件夹并批量上传所有支持的文件（递归子文件夹）"""
    folder = Path(request.folder_path).expanduser().resolve()

    if not folder.exists():
        raise HTTPException(status_code=400, detail=f"文件夹不存在: {folder}")
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"路径不是文件夹: {folder}")

    # 递归收集所有文件
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(Path(root) / filename)

    if not files:
        return {
            "total_found": 0,
            "success": [],
            "failed": [],
            "message": f"未找到支持的文件: {', '.join(SUPPORTED_EXTENSIONS)}",
        }

    # dry_run：只返回文件列表，不做任何保存
    if request.dry_run:
        return {
            "total_found": len(files),
            "success": [{"path": str(f.relative_to(folder))} for f in sorted(files)],
            "failed": [],
        }

    results = {"total_found": len(files), "success": [], "failed": []}

    for file_path in sorted(files):
        try:
            rel_path = file_path.relative_to(folder)
            content = file_path.read_bytes()

            document = await document_service.upload_document(
                file_content=content,
                filename=str(rel_path),
            )

            chunks, vectors = await chunk_service.process_document(
                document_id=document.id,
                chunk_size=request.chunk_size,
                overlap=request.overlap,
                strategy=request.strategy,
            )
            await chunk_service.store_chunks(document.id, chunks, vectors)
            await document_service.update_metadata(
                document.id,
                text_length=sum(c.length for c in chunks),
                chunk_count=len(chunks),
            )
            results["success"].append({
                "path": str(rel_path),
                "doc_id": document.id,
                "chunk_count": len(chunks),
                "status": "processed",
            })

        except Exception as e:
            logger.error(f"处理文件失败: {file_path} — {e}")
            results["failed"].append({"path": str(file_path), "error": str(e)})

        except Exception as e:
            logger.error(f"处理文件失败: {file_path} — {e}")
            results["failed"].append({"path": str(file_path), "error": str(e)})

    logger.info(
        f"文件夹上传完成: {folder} — "
        f"成功 {len(results['success'])}, 失败 {len(results['failed'])}"
    )
    return results
