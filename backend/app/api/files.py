"""文件 API"""
import os
import base64
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models import FileIndex, Project
from app.config import NAS_MOUNT_PATH

router = APIRouter(prefix="/api/files", tags=["files"])


class BrowseResponse(BaseModel):
    path: str
    items: List[dict]


@router.get("/browse", response_model=BrowseResponse)
def browse_directory(
    project_id: int = Query(..., description="项目ID"),
    path: str = Query("", description="目录路径"),
    db: Session = Depends(get_db)
):
    """
    浏览项目目录下的文件和子目录
    
    返回目录下的文件和子目录列表，包含文件名、类型、大小、修改时间
    """
    # 获取项目信息
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 拼接完整路径
    full_path = Path(NAS_MOUNT_PATH) / project.path / path
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="目录不存在")
    
    if not full_path.is_dir():
        raise HTTPException(status_code=400, detail="路径不是目录")
    
    try:
        items = []
        for item in full_path.iterdir():
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": 0 if item.is_dir() else stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            except (PermissionError, OSError) as e:
                # 跳过无法访问的文件
                continue
        
        # 按类型排序（目录在前），再按名称排序
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        relative_path = str(Path(project.path) / path) if path else project.path
        
        return {
            "path": relative_path,
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取目录失败: {str(e)}")


@router.get("/preview/{file_id}")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    预览文件内容
    
    返回文本文件内容或图片的 base64 编码
    """
    # 获取文件索引记录
    file_index = db.query(FileIndex).filter(FileIndex.id == file_id).first()
    if not file_index:
        raise HTTPException(status_code=404, detail="文件索引不存在")
    
    # 获取项目信息
    project = db.query(Project).filter(Project.id == file_index.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 构建完整文件路径
    full_path = Path(NAS_MOUNT_PATH) / file_index.filepath
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        # 根据文件类型返回不同的预览内容
        extension = file_index.extension.lower() if file_index.extension else ""
        
        # 图片文件
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".ico"]
        if extension in image_extensions:
            with open(full_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
                ".ico": "image/x-icon"
            }
            return {
                "type": "image",
                "mime_type": mime_types.get(extension, "image/jpeg"),
                "data": img_data
            }
        
        # 文本文件 - 支持预览
        text_extensions = [".txt", ".md", ".json", ".xml", ".html", ".css", ".js", ".ts", 
                          ".py", ".java", ".c", ".cpp", ".h", ".hpp", ".go", ".rs", ".yaml",
                          ".yml", ".toml", ".ini", ".conf", ".sh", ".bat", ".sql", ".log"]
        if extension in text_extensions or file_index.file_type == "text":
            # 限制预览大小为 100KB
            max_size = 100 * 1024
            file_size = full_path.stat().st_size
            
            if file_size > max_size:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(max_size)
                content += f"\n\n... (文件过大，仅显示前 {max_size // 1024}KB)"
            else:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            
            return {
                "type": "text",
                "encoding": "utf-8",
                "size": file_size,
                "content": content
            }
        
        # 其他类型文件
        return {
            "type": "binary",
            "mime_type": "application/octet-stream",
            "size": full_path.stat().st_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.post("/index")
def index_project(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    对项目进行索引
    
    扫描项目目录下所有文件，并存储到数据库
    """
    # 获取项目信息
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 更新索引状态
    project.index_status = "indexing"
    db.commit()
    
    try:
        # 构建项目完整路径
        full_path = Path(NAS_MOUNT_PATH) / project.path
        
        if not full_path.exists():
            project.index_status = "pending"
            db.commit()
            raise HTTPException(status_code=404, detail="项目目录不存在")
        
        if not full_path.is_dir():
            project.index_status = "pending"
            db.commit()
            raise HTTPException(status_code=400, detail="项目路径不是目录")
        
        # 清空现有索引
        db.query(FileIndex).filter(FileIndex.project_id == project_id).delete()
        
        file_count = 0
        
        # 递归扫描目录
        def scan_directory(dir_path: Path, parent_path: str = ""):
            nonlocal file_count
            
            try:
                for item in dir_path.iterdir():
                    try:
                        relative_path = str(item.relative_to(Path(NAS_MOUNT_PATH) / project.path))
                        
                        if item.is_dir():
                            # 递归扫描子目录
                            scan_directory(item, relative_path)
                        else:
                            # 处理文件
                            stat = item.stat()
                            extension = item.suffix.lower()
                            
                            # 判断文件类型
                            file_type = "binary"
                            if extension in [".txt", ".md", ".json", ".xml", ".html", ".css", ".js", ".ts"]:
                                file_type = "text"
                            elif extension in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".ico"]:
                                file_type = "image"
                            elif extension in [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"]:
                                file_type = "video"
                            elif extension in [".mp3", ".wav", ".flac", ".aac", ".ogg"]:
                                file_type = "audio"
                            elif extension in [".pdf"]:
                                file_type = "document"
                            
                            file_index = FileIndex(
                                project_id=project_id,
                                filename=item.name,
                                filepath=relative_path,
                                file_type=file_type,
                                size=stat.st_size,
                                extension=extension,
                                parent_path=parent_path
                            )
                            db.add(file_index)
                            file_count += 1
                    
                    except (PermissionError, OSError):
                        # 跳过无法访问的文件
                        continue
            
            except (PermissionError, OSError):
                # 跳过无法访问的目录
                return
        
        scan_directory(full_path)
        
        # 提交所有更改
        db.commit()
        
        # 更新项目索引状态和文件数量
        project.index_status = "completed"
        project.file_count = file_count
        db.commit()
        
        return {
            "message": "索引完成",
            "project_id": project_id,
            "file_count": file_count,
            "status": "completed"
        }
    
    except HTTPException:
        project.index_status = "pending"
        db.commit()
        raise
    except Exception as e:
        project.index_status = "pending"
        db.commit()
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.get("")
def get_files(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取项目文件列表"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    """获取文件详情"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件详情失败: {str(e)}")
