"""Favorite 模型"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_index.id"))
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
