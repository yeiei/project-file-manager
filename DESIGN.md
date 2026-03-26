# 项目文件管理系统 - 设计文档

## 1. 系统概述

- **项目名称**: Project File Manager (PFM)
- **类型**: Web 文件管理系统
- **目标**: 管理 2005-2026 年积累的项目文件，支持浏览、搜索、标签、预览等功能
- **用户**: 个人/小团队

## 2. 技术架构

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端 | Python FastAPI | 0.110+ |
| 前端 | Vue3 + NaiveUI | 3.x |
| 数据库 | SQLite | 3.x |
| 搜索 | Whoosh | 2.7 |
| 部署 | Docker | 24.x |

## 3. 目录结构

```
project-file-manager/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── files.py         # 文件 API
│   │   │   ├── search.py        # 搜索 API
│   │   │   ├── tags.py          # 标签 API
│   │   │   ├── favorites.py     # 收藏 API
│   │   │   └── projects.py      # 项目 API
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── file.py          # 文件模型
│   │   │   ├── tag.py           # 标签模型
│   │   │   └── project.py       # 项目模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_service.py  # 文件服务
│   │   │   ├── search_service.py # 搜索服务
│   │   │   └── index_service.py  # 索引服务
│   │   └── core/
│   │       ├── __init__.py
│   │       └── database.py      # 数据库配置
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── api/
│   │   │   └── index.ts
│   │   ├── views/
│   │   │   ├── FileBrowser.vue  # 文件浏览器
│   │   │   ├── Search.vue        # 搜索页面
│   │   │   ├── Projects.vue      # 项目列表
│   │   │   ├── Tags.vue          # 标签管理
│   │   │   ├── Favorites.vue     # 收藏夹
│   │   │   └── Preview.vue       # 预览页面
│   │   ├── components/
│   │   │   ├── FileTree.vue
│   │   │   ├── FileList.vue
│   │   │   ├── TagInput.vue
│   │   │   └── SearchBar.vue
│   │   └── stores/
│   │       └── files.ts
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

## 4. 数据模型

### 4.1 项目 (Project)
```python
class Project:
    id: int
    name: str           # 项目名称
    path: str           # 文件路径
    year: int           # 年份
    category: str      # 分类
    description: str   # 描述
    created_at: datetime
    updated_at: datetime
```

### 4.2 文件索引 (FileIndex)
```python
class FileIndex:
    id: int
    project_id: int     # 所属项目
    filename: str       # 文件名
    filepath: str       # 完整路径
    file_type: str      # 文件类型
    size: int          # 大小
    extension: str     # 扩展名
    content_type: str  # 内容类型
    created_at: datetime
    modified_at: datetime
```

### 4.3 标签 (Tag)
```python
class Tag:
    id: int
    name: str           # 标签名
    color: str         # 颜色
    created_at: datetime
```

### 4.4 文件标签关联 (FileTag)
```python
class FileTag:
    file_id: int
    tag_id: int
```

### 4.5 收藏夹 (Favorite)
```python
class Favorite:
    id: int
    file_id: int
    user_id: int
    created_at: datetime
```

## 5. API 设计

### 5.1 项目 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/projects | 获取项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/:id | 获取项目详情 |
| PUT | /api/projects/:id | 更新项目 |
| DELETE | /api/projects/:id | 删除项目 |

### 5.2 文件 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/files | 获取文件列表 |
| GET | /api/files/:id | 获取文件详情 |
| GET | /api/files/:id/preview | 预览文件 |
| POST | /api/files/index | 索引文件 |

### 5.3 搜索 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/search | 搜索文件 |
| GET | /api/search/suggest | 搜索建议 |

### 5.4 标签 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tags | 获取标签列表 |
| POST | /api/tags | 创建标签 |
| PUT | /api/tags/:id | 更新标签 |
| DELETE | /api/tags/:id | 删除标签 |
| POST | /api/files/:id/tags | 添加标签 |
| DELETE | /api/files/:id/tags/:tag_id | 移除标签 |

### 5.5 收藏 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/favorites | 获取收藏列表 |
| POST | /api/favorites | 添加收藏 |
| DELETE | /api/favorites/:id | 取消收藏 |

## 6. 功能流程

### 6.1 文件浏览
```
1. 用户进入页面 → 调用 /api/projects
2. 选择项目 → 调用 /api/files?project_id=xxx
3. 展开目录 → 调用 /api/files?parent_id=xxx
4. 点击文件 → 预览或下载
```

### 6.2 全文搜索
```
1. 用户输入关键词 → 调用 /api/search?q=xxx
2. 后端查询 Whoosh 索引
3. 返回匹配结果列表
4. 点击结果 → 打开文件
```

### 6.3 标签管理
```
1. 创建标签 → POST /api/tags
2. 给文件加标签 → POST /api/files/:id/tags
3. 按标签筛选 → GET /api/files?tag_id=xxx
```

## 7. 部署配置

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - /home/yei/projects:/data/projects
      - /mnt/nas:/data/nas
    environment:
      - DATABASE_URL=sqlite:///data/files.db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## 8. 开发计划

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 1 | 后端基础框架 + 数据库模型 | 30min |
| 2 | 文件浏览 API + 前端 | 30min |
| 3 | 搜索功能 (Whoosh) | 30min |
| 4 | 标签系统 | 20min |
| 5 | 收藏夹功能 | 20min |
| 6 | 在线预览 | 30min |
| 7 | 测试 + 代码审查 | 30min |

## 9. 验收标准

- [ ] 能浏览本地和 NAS 目录
- [ ] 能搜索文件名和内容
- [ ] 能创建和管理标签
- [ ] 能收藏常用文件
- [ ] 能在线预览图片/代码
- [ ] Docker 一键部署
- [ ] 界面美观易用
