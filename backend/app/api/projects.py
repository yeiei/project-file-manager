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
        base_dir: 基础目录，路径不应超出此目录（仅用于相对路径）
    
    Returns:
        bool: 路径是否安全
    
    Raises:
        HTTPException: 路径不安全时抛出异常
    """
    # 解析路径并规范化
    try:
        # 如果是绝对路径，直接解析；如果是相对路径，基于 base_dir 解析
        if Path(path).is_absolute():
            resolved_path = Path(path).resolve()
            # 对于绝对路径，只检查路径是否存在且可访问
            if not resolved_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail="路径不存在"
                )
            return True
        else:
            # 相对路径：基于 base_dir 解析
            full_path = Path(base_dir) / path
            resolved_path = full_path.resolve()
            base_path = Path(base_dir).resolve()
            
            # 检查是否超出基础目录
            if not str(resolved_path).startswith(str(base_path)):
                raise HTTPException(
                    status_code=400,
                    detail="路径不允许超出允许的目录范围"
                )
            
            # 检查路径是否存在
            if not resolved_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail="路径不存在"
                )
            
            return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="路径格式无效")


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    path: str = Field(..., min_length=1, max_length=500, description="项目路径")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="项目年份")
    category: Optional[str] = Field(None, max_length=100, description="项目分类")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")
    # 新增字段
    owner: Optional[str] = Field(None, max_length=100, description="负责人")
    debugger: Optional[str] = Field(None, max_length=100, description="调试人")
    improvements: Optional[str] = Field(None, description="改进内容")

    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """验证路径安全性"""
        # 允许绝对路径和相对路径
        # 实际的安全性检查由 validate_path_safety 函数完成
        
        # 检查危险字符（不在安全路径中的字符）
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
    # 新增字段
    owner: Optional[str] = None
    debugger: Optional[str] = None
    improvements: Optional[str] = None
    # 原有字段
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
                "owner": p.owner,
                "debugger": p.debugger,
                "improvements": p.improvements,
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
            owner=project.owner,
            debugger=project.debugger,
            improvements=project.improvements,
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
            "owner": db_project.owner,
            "debugger": db_project.debugger,
            "improvements": db_project.improvements,
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


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="项目名称")
    path: Optional[str] = Field(None, min_length=1, max_length=500, description="项目路径")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="项目年份")
    category: Optional[str] = Field(None, max_length=100, description="项目分类")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")
    owner: Optional[str] = Field(None, max_length=100, description="负责人")
    debugger: Optional[str] = Field(None, max_length=100, description="调试人")
    improvements: Optional[str] = Field(None, description="改进内容")


@router.put("/{project_id}")
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 如果提供了新路径，验证路径安全性
    if project_update.path is not None and project_update.path != project.path:
        validate_path_safety(project_update.path)
    
    # 更新字段（只更新非 None 的字段）
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "name": project.name,
        "path": project.path,
        "year": project.year,
        "category": project.category,
        "description": project.description,
        "owner": project.owner,
        "debugger": project.debugger,
        "improvements": project.improvements,
        "index_status": project.index_status,
        "file_count": project.file_count,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }
