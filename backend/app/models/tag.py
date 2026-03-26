"""Tag 模型"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from datetime import datetime

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


# 文件标签关联表
file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file_index.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)
