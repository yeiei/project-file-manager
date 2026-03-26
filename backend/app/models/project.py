"""Project 模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False)
    year = Column(Integer)
    category = Column(String(100))
    description = Column(Text)
    index_status = Column(String(20), default="pending")  # 'pending', 'indexing', 'completed'
    file_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
