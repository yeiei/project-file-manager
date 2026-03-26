"""搜索 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.search import search_files, rebuild_index

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResult(BaseModel):
    id: int
    filename: str
    filepath: str
    file_type: str
    extension: str
    project_id: int
    score: float


@router.get("", response_model=List[SearchResult])
def search(
    q: str = Query(..., description="搜索关键词", min_length=1),
    project_id: Optional[int] = Query(None, description="项目ID过滤"),
    limit: int = Query(50, description="返回结果数量限制", ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    全文搜索文件
    
    支持按文件名和文件内容进行搜索，返回匹配的结果列表
    """
    try:
        results = search_files(query=q, project_id=project_id, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/rebuild")
def rebuild_search_index(
    project_id: Optional[int] = Query(None, description="项目ID（可选）"),
    db: Session = Depends(get_db)
):
    """
    重建搜索索引
    
    扫描数据库中的文件记录并重新建立搜索索引
    """
    try:
        count = rebuild_index(project_id=project_id)
        return {
            "message": "索引重建完成",
            "indexed_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引重建失败: {str(e)}")
