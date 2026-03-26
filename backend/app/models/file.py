"""FileIndex 模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class FileIndex(Base):
    __tablename__ = "file_index"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1024), nullable=False)
    file_type = Column(String(50))
    size = Column(Integer)
    extension = Column(String(20))
    parent_path = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
