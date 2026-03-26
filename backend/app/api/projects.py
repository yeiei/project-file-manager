"""项目 API"""
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Project

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    path: str
    year: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    year: Optional[int]
    category: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@router.get("", response_model=List[dict])
def get_projects(db: Session = Depends(get_db)):
    """获取项目列表"""
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "path": p.path,
            "year": p.year,
            "category": p.category,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in projects
    ]


@router.post("")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建项目"""
    db_project = Project(
        name=project.name,
        path=project.path,
        year=project.year,
        category=project.category,
        description=project.description
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
        "created_at": db_project.created_at.isoformat() if db_project.created_at else None,
        "updated_at": db_project.updated_at.isoformat() if db_project.updated_at else None,
    }
