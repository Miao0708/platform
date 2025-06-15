"""
知识库相关API数据模式
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    """创建知识库的请求模式"""
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model: str = Field("text-embedding-ada-002", description="嵌入模型")
    chunk_size: int = Field(1000, description="文档切片大小", ge=100, le=4000)
    chunk_overlap: int = Field(200, description="切片重叠大小", ge=0, le=1000)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "技术文档库",
                    "description": "存储技术文档和API文档",
                    "embedding_model": "text-embedding-ada-002",
                    "chunk_size": 1000,
                    "chunk_overlap": 200
                }
            ]
        }
    }


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库的请求模式"""
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model: Optional[str] = Field(None, description="嵌入模型")
    chunk_size: Optional[int] = Field(None, description="文档切片大小", ge=100, le=4000)
    chunk_overlap: Optional[int] = Field(None, description="切片重叠大小", ge=0, le=1000)
    is_active: Optional[bool] = Field(None, description="是否激活")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应模式"""
    id: int
    name: str
    description: Optional[str]
    collection_name: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """文档上传响应模式"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    """文档响应模式"""
    id: int
    knowledge_base_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    content_hash: str
    status: str
    error_message: Optional[str]
    doc_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class DocumentChunkResponse(BaseModel):
    """文档切片响应模式"""
    id: int
    document_id: int
    chunk_index: int
    content: str
    content_hash: str
    token_count: Optional[int]
    embedding_id: Optional[str]
    chunk_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class RAGSearchRequest(BaseModel):
    """RAG搜索请求模式"""
    query: str = Field(..., description="搜索查询")
    knowledge_base_id: int = Field(..., description="知识库ID")
    top_k: int = Field(5, description="返回结果数量", ge=1, le=20)
    score_threshold: float = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    include_metadata: bool = Field(True, description="是否包含元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "如何使用FastAPI创建API",
                    "knowledge_base_id": 1,
                    "top_k": 5,
                    "score_threshold": 0.7,
                    "include_metadata": True
                }
            ]
        }
    }


class RAGSearchResult(BaseModel):
    """RAG搜索结果项"""
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相似度分数")
    document_id: int = Field(..., description="文档ID")
    chunk_index: int = Field(..., description="切片索引")
    chunk_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    document_filename: Optional[str] = Field(None, description="文档文件名")


class RAGSearchResponse(BaseModel):
    """RAG搜索响应模式"""
    query: str = Field(..., description="搜索查询")
    results: List[RAGSearchResult] = Field(..., description="搜索结果")
    total_results: int = Field(..., description="总结果数")
    search_time: float = Field(..., description="搜索耗时（秒）")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "如何使用FastAPI创建API",
                    "results": [
                        {
                            "content": "FastAPI是一个现代、快速的Web框架...",
                            "score": 0.95,
                            "document_id": 1,
                            "chunk_index": 0,
                            "chunk_metadata": {"page": 1, "section": "介绍"},
                            "document_filename": "fastapi_guide.pdf"
                        }
                    ],
                    "total_results": 1,
                    "search_time": 0.123
                }
            ]
        }
    }


class DocumentProcessingStatus(BaseModel):
    """文档处理状态"""
    document_id: int
    status: str
    progress: float = Field(description="处理进度 0-100")
    message: str
    chunks_created: int = Field(default=0, description="已创建的切片数量")
    total_chunks: Optional[int] = Field(None, description="总切片数量")


class KnowledgeBaseStats(BaseModel):
    """知识库统计信息"""
    knowledge_base_id: int
    total_documents: int
    total_chunks: int
    total_size: int = Field(description="总文件大小（字节）")
    processing_documents: int
    failed_documents: int
    supported_file_types: List[str]
