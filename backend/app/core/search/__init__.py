"""Whoosh 全文搜索引擎"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.writing import AsyncWriter
import threading

from app.config import BASE_DIR
from app.core.database import SessionLocal
from app.models import FileIndex

# 索引目录
INDEX_DIR = BASE_DIR / "data" / "whoosh_index"

# Whoosh Schema 定义
SEARCH_SCHEMA = Schema(
    id=ID(stored=True, unique=True),
    filename=TEXT(stored=True, sortable=True),
    filepath=TEXT(stored=True),
    content=TEXT(stored=True),
    file_type=KEYWORD(stored=True),
    extension=KEYWORD(stored=True),
    project_id=NUMERIC(stored=True),
)

# 线程锁，用于索引写入
_index_lock = threading.Lock()


def get_index():
    """获取或创建索引"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    if index.exists_in(str(INDEX_DIR)):
        return index.open_dir(str(INDEX_DIR))
    else:
        return index.create_in(str(INDEX_DIR), SEARCH_SCHEMA)


def get_or_create_index():
    """获取或创建索引（线程安全）"""
    with _index_lock:
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        
        if index.exists_in(str(INDEX_DIR)):
            ix = index.open_dir(str(INDEX_DIR))
        else:
            ix = index.create_in(str(INDEX_DIR), SEARCH_SCHEMA)
        
        return ix


def add_file_to_index(file_index: FileIndex, content: str = ""):
    """
    将文件添加到搜索索引
    
    Args:
        file_index: FileIndex 模型实例
        content: 文件内容（可选）
    """
    ix = get_or_create_index()
    writer = ix.writer()
    
    try:
        writer.update_document(
            id=str(file_index.id),
            filename=file_index.filename,
            filepath=file_index.filepath,
            content=content or "",
            file_type=file_index.file_type or "",
            extension=file_index.extension or "",
            project_id=file_index.project_id,
        )
        writer.commit()
    except Exception as e:
        writer.cancel()
        raise e


def remove_file_from_index(file_id: int):
    """从索引中移除文件"""
    ix = get_or_create_index()
    writer = ix.writer()
    
    try:
        writer.delete_by_term("id", str(file_id))
        writer.commit()
    except Exception as e:
        writer.cancel()
        raise e


def search_files(
    query: str,
    project_id: Optional[int] = None,
    limit: int = 50
) -> List[Dict]:
    """
    搜索文件
    
    Args:
        query: 搜索关键词
        project_id: 项目ID过滤（可选）
        limit: 返回结果数量限制
    
    Returns:
        匹配结果列表
    """
    ix = get_or_create_index()
    
    results = []
    with ix.searcher() as searcher:
        # 使用多字段搜索，同时搜索文件名和内容
        parser = MultifieldParser(["filename", "content"], schema=SEARCH_SCHEMA)
        parsed_query = parser.parse(query)
        
        search_results = searcher.search(parsed_query, limit=limit)
        
        for hit in search_results:
            result = {
                "id": int(hit["id"]),
                "filename": hit["filename"],
                "filepath": hit["filepath"],
                "file_type": hit["file_type"],
                "extension": hit["extension"],
                "project_id": hit["project_id"],
                "score": hit.score,
            }
            
            # 如果指定了项目ID过滤
            if project_id is not None and result["project_id"] != project_id:
                continue
                
            results.append(result)
    
    return results


def rebuild_index(project_id: Optional[int] = None):
    """
    重建搜索索引
    
    Args:
        project_id: 项目ID（可选，为None时重建所有项目）
    """
    db = SessionLocal()
    try:
        ix = get_or_create_index()
        writer = ix.writer()
        
        # 查询文件
        query = db.query(FileIndex)
        if project_id:
            query = query.filter(FileIndex.project_id == project_id)
        
        files = query.all()
        
        for file in files:
            # 尝试读取文件内容
            content = ""
            try:
                from app.config import NAS_MOUNT_PATH
                from pathlib import Path
                full_path = Path(NAS_MOUNT_PATH) / file.filepath
                if full_path.exists() and full_path.is_file():
                    # 只索引文本文件内容
                    text_extensions = [".txt", ".md", ".json", ".xml", ".html", ".css", ".js", ".ts", 
                                     ".py", ".java", ".c", ".cpp", ".h", ".hpp", ".go", ".rs", ".yaml",
                                     ".yml", ".toml", ".ini", ".conf", ".sh", ".bat", ".sql", ".log"]
                    if file.extension and file.extension.lower() in text_extensions:
                        # 限制内容大小为50KB
                        if full_path.stat().st_size < 50 * 1024:
                            try:
                                content = full_path.read_text(encoding="utf-8", errors="ignore")
                                content = content[:50000]  # 限制内容长度
                            except:
                                content = ""
            except Exception:
                pass
            
            writer.update_document(
                id=str(file.id),
                filename=file.filename,
                filepath=file.filepath,
                content=content,
                file_type=file.file_type or "",
                extension=file.extension or "",
                project_id=file.project_id,
            )
        
        writer.commit()
        return len(files)
    except Exception as e:
        writer.cancel()
        raise e
    finally:
        db.close()
