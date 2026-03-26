"""标签 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Tag, FileIndex
from app.models.tag import file_tags

router = APIRouter(prefix="/api/tags", tags=["tags"])


# Pydantic 模型
class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class FileTagResponse(BaseModel):
    id: int
    filename: str
    filepath: str


@router.get("", response_model=List[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    """
    获取标签列表
    
    返回所有已创建的标签
    """
    tags = db.query(Tag).order_by(Tag.created_at.desc()).all()
    return [
        {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat() if tag.created_at else ""
        }
        for tag in tags
    ]


@router.post("", response_model=TagResponse)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    创建标签
    
    创建一个新的标签
    """
    # 检查是否已存在同名标签
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    
    new_tag = Tag(name=tag.name, color=tag.color)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return {
        "id": new_tag.id,
        "name": new_tag.name,
        "color": new_tag.color,
        "created_at": new_tag.created_at.isoformat() if new_tag.created_at else ""
    }


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db)
):
    """
    更新标签
    
    更新标签的名称或颜色
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    # 如果更新名称，检查是否已存在
    if tag_update.name and tag_update.name != tag.name:
        existing = db.query(Tag).filter(Tag.name == tag_update.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="标签名称已存在")
        tag.name = tag_update.name
    
    if tag_update.color:
        tag.color = tag_update.color
    
    db.commit()
    db.refresh(tag)
    
    return {
        "id": tag.id,
        "name": tag.name,
        "color": tag.color,
        "created_at": tag.created_at.isoformat() if tag.created_at else ""
    }


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    删除标签
    
    删除指定标签，同时清除所有关联的文件标签关系
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    db.delete(tag)
    db.commit()
    
    return {"message": "标签已删除"}


@router.get("/{tag_id}/files", response_model=List[FileTagResponse])
def get_tag_files(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    获取标签关联的文件
    
    返回所有使用该标签的文件
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    files = tag.files
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "filepath": f.filepath
        }
        for f in files
    ]


# 文件标签关联 API
@router.post("/files/{file_id}/tags")
def add_tag_to_file(
    file_id: int,
    tag_id: int = Query(..., description="标签ID"),
    db: Session = Depends(get_db)
):
    """
    给文件添加标签
    
    为指定文件添加一个标签
    """
    # 检查文件是否存在
    file = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查标签是否存在
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    # 检查是否已关联
    if tag in file.tags:
        raise HTTPException(status_code=400, detail="文件已添加该标签")
    
    # 添加关联
    file.tags.append(tag)
    db.commit()
    
    return {"message": "标签已添加到文件"}


@router.delete("/files/{file_id}/tags/{tag_id}")
def remove_tag_from_file(
    file_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    移除文件标签
    
    从指定文件移除一个标签
    """
    # 检查文件是否存在
    file = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查标签是否存在
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    # 检查是否已关联
    if tag not in file.tags:
        raise HTTPException(status_code=400, detail="文件未添加该标签")
    
    # 移除关联
    file.tags.remove(tag)
    db.commit()
    
    return {"message": "标签已从文件移除"}


@router.get("/files/{file_id}/tags", response_model=List[TagResponse])
def get_file_tags(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文件的所有标签
    
    返回指定文件关联的所有标签
    """
    file = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return [
        {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat() if tag.created_at else ""
        }
        for tag in file.tags
    ]
