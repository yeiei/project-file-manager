"""项目 API"""
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Project

router = APIRouter(prefix="/api/projects", tags=["projects"])


def validate_path_safety(path: str, base_dir: str = "/mnt/nas") -> bool:
    """
    验证路径安全性，防止路径遍历攻击
    
    Args:
        path: 用户输入的路径
        base_dir: 基础目录，路径不应超出此目录
    
    Returns:
        bool: 路径是否安全
    
    Raises:
        HTTPException: 路径不安全时抛出异常
    """
    # 解析路径并规范化
    try:
        # 将路径转换为绝对路径并规范化（解析 .. 和 .）
        full_path = Path(base_dir) / path
        resolved_path = full_path.resolve()
        base_path = Path(base_dir).resolve()
        
        # 检查是否超出基础目录
        if not str(resolved_path).startswith(str(base_path)):
            raise HTTPException(
                status_code=400,
                detail="路径不允许超出允许的目录范围"
            )
        
        # 检查路径中是否包含危险字符或模式
        dangerous_patterns = ["../", "..\\", "~", "$"]
        for pattern in dangerous_patterns:
            if pattern in path:
                raise HTTPException(
                    status_code=400,
                    detail=f"路径包含不安全字符: {pattern}"
                )
        
        return True
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail="路径格式无效")


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    path: str = Field(..., min_length=1, max_length=500, description="项目路径")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="项目年份")
    category: Optional[str] = Field(None, max_length=100, description="项目分类")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")

    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """验证路径安全性"""
        # 检查绝对路径
        if v.startswith('/') or v.startswith('\\'):
            raise ValueError("路径不能是绝对路径")
        
        # 检查路径遍历
        if '..' in v:
            raise ValueError("路径不能包含 ..")
        
        # 检查危险字符
        if any(char in v for char in ['$', '`', '|', ';', '&', '\n', '\r']):
            raise ValueError("路径包含非法字符")
        
        return v


class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    year: Optional[int]
    category: Optional[str]
    description: Optional[str]
    index_status: Optional[str] = "pending"
    file_count: Optional[int] = 0
    created_at: Optional[str]
    updated_at: Optional[str]


@router.get("", response_model=List[dict])
def get_projects(db: Session = Depends(get_db)):
    """获取项目列表"""
    try:
        projects = db.query(Project).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "path": p.path,
                "year": p.year,
                "category": p.category,
                "description": p.description,
                "index_status": p.index_status or "pending",
                "file_count": p.file_count or 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")


@router.post("")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建项目"""
    try:
        # 验证路径安全性
        validate_path_safety(project.path)
        
        db_project = Project(
            name=project.name,
            path=project.path,
            year=project.year,
            category=project.category,
            description=project.description,
            index_status="pending",
            file_count=0
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return {
            "id": db_project.id,
            "name": db_project.name,
            "path": db_project.path,
            "year": db_project.year,
            "category": db_project.category,
            "description": db_project.description,
            "index_status": db_project.index_status,
            "file_count": db_project.file_count,
            "created_at": db_project.created_at.isoformat() if db_project.created_at else None,
            "updated_at": db_project.updated_at.isoformat() if db_project.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(project)
    db.commit()
    return {"message": "项目删除成功"}
