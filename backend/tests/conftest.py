"""pytest 配置文件"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import tempfile

# 确保 app 模块可以被导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 先导入模型，这会注册所有表
from app.models import Project, FileIndex, Tag, Favorite, file_tags
import app.core.database as db_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 使用临时文件数据库
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()
TEST_DB_URL = f"sqlite:///{temp_db.name}"

# 替换 engine 和 SessionLocal
new_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
db_module.engine = new_engine
db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)

# 创建所有表
db_module.Base.metadata.create_all(bind=new_engine)

# 覆盖 get_db 依赖
def override_get_db():
    db = db_module.SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.main import app
app.dependency_overrides[db_module.get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """每个测试前清空表"""
    db = db_module.SessionLocal()
    try:
        db.query(FileIndex).delete()
        db.query(Project).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Reset error: {e}")
    finally:
        db.close()
    
    yield
