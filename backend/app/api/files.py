"""文件 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import FileIndex

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("")
def get_files(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取项目文件列表"""
    files = db.query(FileIndex).filter(FileIndex.project_id == project_id).all()
    return [
        {
            "id": f.id,
            "project_id": f.project_id,
            "filename": f.filename,
            "filepath": f.filepath,
            "file_type": f.file_type,
            "size": f.size,
            "extension": f.extension,
            "parent_path": f.parent_path,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "modified_at": f.modified_at.isoformat() if f.modified_at else None,
        }
        for f in files
    ]


@router.get("/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    """获取文件详情"""
    file = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    return {
        "id": file.id,
        "project_id": file.project_id,
        "filename": file.filename,
        "filepath": file.filepath,
        "file_type": file.file_type,
        "size": file.size,
        "extension": file.extension,
        "parent_path": file.parent_path,
        "created_at": file.created_at.isoformat() if file.created_at else None,
        "modified_at": file.modified_at.isoformat() if file.modified_at else None,
    }
