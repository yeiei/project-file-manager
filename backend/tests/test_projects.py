"""测试项目 API"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


class TestProjectsAPI:
    def test_get_projects_empty(self, client):
        """获取项目列表 - 空列表"""
        response = client.get("/api/projects")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_project(self, client):
        """创建项目"""
        data = {
            "name": "测试项目",
            "path": "projects/test",
            "year": 2024,
            "category": "视频",
            "description": "测试描述"
        }
        response = client.post("/api/projects", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == data["name"]
        assert result["path"] == data["path"]
        assert "id" in result

    def test_get_projects_after_create(self, client):
        """获取项目列表 - 有数据"""
        # 先创建一个项目
        data = {
            "name": "测试项目2",
            "path": "projects/test2",
            "year": 2024,
            "category": "图片"
        }
        client.post("/api/projects", json=data)
        
        response = client.get("/api/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) >= 1
