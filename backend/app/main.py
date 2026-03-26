"""FastAPI 应用入口"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.api import projects, files, search, tags, favorites, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时清理资源


app = FastAPI(
    title="项目文件管理系统 API",
    description="用于管理项目文件的 REST API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS - 从环境变量读取，允许特定来源
def get_cors_origins() -> list:
    """获取 CORS 允许的来源列表"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    if cors_env:
        # 支持逗号分隔的多个域名
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    # 默认允许所有来源（开发环境）
    return ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(files.router)
app.include_router(search.router)
app.include_router(tags.router)
app.include_router(favorites.router)


@app.get("/")
def root():
    """根路径"""
    return {"message": "项目文件管理系统 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}
