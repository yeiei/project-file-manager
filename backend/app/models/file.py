"""FileIndex 模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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
    content = Column(Text)  # 存储文件内容用于搜索（文本文件）
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    tags = relationship("Tag", secondary="file_tags", back_populates="files")
    favorites = relationship("Favorite", back_populates="file", cascade="all, delete-orphan")
