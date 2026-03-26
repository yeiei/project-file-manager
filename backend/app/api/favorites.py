"""收藏 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Favorite, FileIndex

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


# Pydantic 模型
class FavoriteCreate(BaseModel):
    file_id: int
    user_id: Optional[int] = 1


class FavoriteResponse(BaseModel):
    id: int
    file_id: int
    user_id: int
    created_at: str

    class Config:
        from_attributes = True


class FavoriteWithFile(BaseModel):
    id: int
    file_id: int
    user_id: int
    created_at: str
    file: dict


@router.get("", response_model=List[FavoriteWithFile])
def get_favorites(
    user_id: Optional[int] = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取收藏列表
    
    返回当前用户收藏的所有文件
    """
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).all()
    
    result = []
    for fav in favorites:
        file = db.query(FileIndex).filter(FileIndex.id == fav.file_id).first()
        if file:
            result.append({
                "id": fav.id,
                "file_id": fav.file_id,
                "user_id": fav.user_id,
                "created_at": fav.created_at.isoformat() if fav.created_at else "",
                "file": {
                    "id": file.id,
                    "filename": file.filename,
                    "filepath": file.filepath,
                    "file_type": file.file_type,
                    "extension": file.extension,
                    "size": file.size,
                }
            })
    
    return result


@router.post("", response_model=FavoriteResponse)
def add_favorite(
    favorite: FavoriteCreate,
    db: Session = Depends(get_db)
):
    """
    添加收藏
    
    将文件添加到收藏列表
    """
    # 检查文件是否存在
    file = db.query(FileIndex).filter(FileIndex.id == favorite.file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.file_id == favorite.file_id,
        Favorite.user_id == favorite.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="文件已收藏")
    
    new_favorite = Favorite(
        file_id=favorite.file_id,
        user_id=favorite.user_id or 1
    )
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    
    return {
        "id": new_favorite.id,
        "file_id": new_favorite.file_id,
        "user_id": new_favorite.user_id,
        "created_at": new_favorite.created_at.isoformat() if new_favorite.created_at else ""
    }


@router.delete("/{favorite_id}")
def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db)
):
    """
    取消收藏
    
    从收藏列表中移除
    """
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "已取消收藏"}


@router.get("/files/{file_id}/favorite")
def check_favorite(
    file_id: int,
    user_id: int = Query(1, description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    检查文件是否已收藏
    
    返回指定文件的收藏状态
    """
    # 检查文件是否存在
    file = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    favorite = db.query(Favorite).filter(
        Favorite.file_id == file_id,
        Favorite.user_id == user_id
    ).first()
    
    return {
        "file_id": file_id,
        "is_favorited": favorite is not None,
        "favorite_id": favorite.id if favorite else None
    }
