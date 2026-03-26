"""测试文件 API"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_project(client):
    """创建测试项目"""
    data = {
        "name": "文件测试项目",
        "path": "/mnt/nas/projects/filetest",
        "year": 2024,
        "category": "视频"
    }
    response = client.post("/api/projects", json=data)
    return response.json()


class TestFilesAPI:
    def test_get_files_empty(self, client, test_project):
        """获取文件列表 - 空列表"""
        response = client.get(f"/api/files?project_id={test_project['id']}")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_files_missing_project_id(self, client):
        """获取文件列表 - 缺少 project_id"""
        response = client.get("/api/files")
        assert response.status_code == 422  # FastAPI 会返回验证错误

    def test_get_file_detail(self, client, test_project):
        """获取文件详情 - 不存在"""
        response = client.get("/api/files/99999")
        assert response.status_code == 404
