"""Favorite 模型"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_index.id"))
    user_id = Column(Integer, default=1)  # 默认用户ID
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    file = relationship("FileIndex", back_populates="favorites")
