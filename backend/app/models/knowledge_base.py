"""
知识库相关数据模型
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class KnowledgeBase(BaseModel, table=True):
    """知识库模型"""
    
    __tablename__ = "knowledge_bases"
    
    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    collection_name: str = Field(description="ChromaDB集合名称", unique=True, index=True)
    embedding_model: str = Field(default="text-embedding-ada-002", description="嵌入模型")
    chunk_size: int = Field(default=1000, description="文档切片大小")
    chunk_overlap: int = Field(default=200, description="切片重叠大小")
    is_active: bool = Field(default=True, description="是否激活")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "技术文档库",
                    "description": "存储技术文档和API文档",
                    "collection_name": "tech_docs_collection",
                    "embedding_model": "text-embedding-ada-002",
                    "chunk_size": 1000,
                    "chunk_overlap": 200,
                    "is_active": True
                }
            ]
        }
    }


class Document(BaseModel, table=True):
    """文档模型"""
    
    __tablename__ = "documents"
    
    knowledge_base_id: int = Field(foreign_key="knowledge_bases.id", description="所属知识库ID")
    filename: str = Field(description="文件名")
    original_filename: str = Field(description="原始文件名")
    file_path: str = Field(description="文件存储路径")
    file_size: int = Field(description="文件大小（字节）")
    file_type: str = Field(description="文件类型")
    content_hash: str = Field(description="文件内容哈希", index=True)
    status: str = Field(default="pending", description="处理状态：pending, processing, completed, failed")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    doc_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="文档元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "knowledge_base_id": 1,
                    "filename": "api_doc_20240101.pdf",
                    "original_filename": "API文档.pdf",
                    "file_path": "/uploads/kb1/api_doc_20240101.pdf",
                    "file_size": 1024000,
                    "file_type": "pdf",
                    "content_hash": "sha256_hash_here",
                    "status": "completed",
                    "doc_metadata": {
                        "author": "技术团队",
                        "version": "1.0",
                        "tags": ["API", "文档"]
                    }
                }
            ]
        }
    }


class DocumentChunk(BaseModel, table=True):
    """文档切片模型"""
    
    __tablename__ = "document_chunks"
    
    document_id: int = Field(foreign_key="documents.id", description="所属文档ID")
    chunk_index: int = Field(description="切片索引")
    content: str = Field(sa_column=Column(Text), description="切片内容")
    content_hash: str = Field(description="切片内容哈希", index=True)
    token_count: Optional[int] = Field(default=None, description="Token数量")
    embedding_id: Optional[str] = Field(default=None, description="ChromaDB中的嵌入ID")
    chunk_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="切片元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_id": 1,
                    "chunk_index": 0,
                    "content": "这是文档的第一个切片内容...",
                    "content_hash": "chunk_hash_here",
                    "token_count": 150,
                    "embedding_id": "doc1_chunk0",
                    "chunk_metadata": {
                        "page": 1,
                        "section": "介绍"
                    }
                }
            ]
        }
    }
