"""切片管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Query

from src.application.services import ChunkService
from src.application.schemas import ChunkListResponse
from src.api.deps import get_chunk_service
from src.infrastructure.logging.setup import get_logger

router = APIRouter(prefix="/chunks", tags=["切片管理"])
logger = get_logger(__name__)


@router.get("/{document_id}", response_model=ChunkListResponse)
async def get_chunks(
    document_id: str,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """获取文档的切片"""
    try:
        chunks = await chunk_service.get_chunks_by_document(document_id)
        
        return ChunkListResponse(
            document_id=document_id,
            chunks=[chunk_service.to_response(c).model_dump() for c in chunks],
            total=len(chunks),
        )
        
    except Exception as e:
        logger.error(f"获取切片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
