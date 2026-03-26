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

# NAS 挂载路径（可配置）
NAS_MOUNT_PATH = os.getenv("NAS_MOUNT_PATH", "/mnt/nas")

# CORS 配置
# 格式: 逗号分隔的域名列表，如: "http://localhost:3000,http://example.com"
# 空字符串或未设置时使用默认值
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")

# 安全配置
# 是否允许凭证（cookies）在 CORS 请求中传递
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# API 密钥配置（可选）
API_KEY = os.getenv("API_KEY", "")

# 创建必要目录
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
