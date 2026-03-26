"""配置文件"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_PATH = BASE_DIR / "data" / "filemanager.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 上传目录
UPLOAD_DIR = BASE_DIR / "uploads"

# NAS 挂载路径
NAS_MOUNT_PATH = "/mnt/nas"

# 创建必要目录
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
