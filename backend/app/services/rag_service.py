"""
RAG（检索增强生成）服务
处理知识库搜索和检索功能
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from app.schemas.knowledge_base import RAGSearchRequest, RAGSearchResponse, RAGSearchResult
from app.core.vector_store import chroma_manager
from app.services.document_service import document_processor


class RAGService:
    """RAG服务类"""
    
    def __init__(self):
        """初始化RAG服务"""
        pass
    
    def search_knowledge_base(
        self, 
        db: Session, 
        search_request: RAGSearchRequest
    ) -> RAGSearchResponse:
        """
        在知识库中搜索相关内容
        
        Args:
            db: 数据库会话
            search_request: 搜索请求
            
        Returns:
            搜索响应
        """
        start_time = time.time()
        
        # 获取知识库信息
        kb = db.get(KnowledgeBase, search_request.knowledge_base_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        if not kb.is_active:
            raise ValueError("知识库未激活")
        
        # 在ChromaDB中搜索
        search_results = chroma_manager.search_documents(
            collection_name=kb.collection_name,
            query_texts=[search_request.query],
            n_results=search_request.top_k
        )
        
        if not search_results or not search_results.get('documents'):
            return RAGSearchResponse(
                query=search_request.query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time
            )
        
        # 处理搜索结果
        results = self._process_search_results(
            db=db,
            search_results=search_results,
            score_threshold=search_request.score_threshold,
            include_metadata=search_request.include_metadata
        )
        
        search_time = time.time() - start_time
        
        return RAGSearchResponse(
            query=search_request.query,
            results=results,
            total_results=len(results),
            search_time=search_time
        )
    
    def _process_search_results(
        self,
        db: Session,
        search_results: Dict[str, Any],
        score_threshold: float,
        include_metadata: bool
    ) -> List[RAGSearchResult]:
        """
        处理ChromaDB搜索结果
        
        Args:
            db: 数据库会话
            search_results: ChromaDB搜索结果
            score_threshold: 分数阈值
            include_metadata: 是否包含元数据
            
        Returns:
            处理后的搜索结果列表
        """
        results = []
        
        # ChromaDB返回的是嵌套列表，第一层是查询，第二层是结果
        documents = search_results['documents'][0]  # 第一个查询的文档
        metadatas = search_results['metadatas'][0]  # 第一个查询的元数据
        distances = search_results['distances'][0]  # 第一个查询的距离
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # 将距离转换为相似度分数（距离越小，相似度越高）
            # ChromaDB使用余弦距离，范围是0-2，转换为0-1的相似度分数
            similarity_score = max(0, 1 - distance / 2)
            
            # 过滤低分结果
            if similarity_score < score_threshold:
                continue
            
            # 从元数据中提取信息
            document_id = metadata.get('document_id')
            chunk_index = metadata.get('chunk_index', 0)
            
            # 获取文档信息
            document_filename = None
            if document_id and include_metadata:
                document_obj = db.get(Document, document_id)
                if document_obj:
                    document_filename = document_obj.original_filename
            
            # 构建搜索结果
            result = RAGSearchResult(
                content=doc,
                score=similarity_score,
                document_id=document_id or 0,
                chunk_index=chunk_index,
                metadata=metadata if include_metadata else None,
                document_filename=document_filename
            )
            
            results.append(result)
        
        # 按分数降序排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def get_similar_chunks(
        self,
        db: Session,
        knowledge_base_id: int,
        content: str,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[RAGSearchResult]:
        """
        获取与给定内容相似的文档切片
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            content: 内容文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            相似切片列表
        """
        search_request = RAGSearchRequest(
            query=content,
            knowledge_base_id=knowledge_base_id,
            top_k=top_k,
            score_threshold=score_threshold,
            include_metadata=True
        )
        
        response = self.search_knowledge_base(db, search_request)
        return response.results
    
    def get_context_for_query(
        self,
        db: Session,
        knowledge_base_id: int,
        query: str,
        max_context_length: int = 4000,
        top_k: int = 10
    ) -> Tuple[str, List[RAGSearchResult]]:
        """
        为查询获取上下文信息
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            query: 查询文本
            max_context_length: 最大上下文长度
            top_k: 搜索结果数量
            
        Returns:
            (合并的上下文文本, 搜索结果列表)
        """
        # 搜索相关内容
        search_request = RAGSearchRequest(
            query=query,
            knowledge_base_id=knowledge_base_id,
            top_k=top_k,
            score_threshold=0.6,
            include_metadata=True
        )
        
        response = self.search_knowledge_base(db, search_request)
        
        # 合并上下文
        context_parts = []
        current_length = 0
        
        for result in response.results:
            content_length = len(result.content)
            
            # 检查是否超过最大长度
            if current_length + content_length > max_context_length:
                break
            
            context_parts.append(result.content)
            current_length += content_length
        
        # 合并上下文
        context = "\n\n".join(context_parts)
        
        return context, response.results
    
    def validate_knowledge_base_access(
        self, 
        db: Session, 
        knowledge_base_id: int
    ) -> KnowledgeBase:
        """
        验证知识库访问权限
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            
        Returns:
            知识库对象
            
        Raises:
            ValueError: 知识库不存在或未激活
        """
        kb = db.get(KnowledgeBase, knowledge_base_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        if not kb.is_active:
            raise ValueError("知识库未激活")
        
        return kb
    
    def get_knowledge_base_summary(
        self, 
        db: Session, 
        knowledge_base_id: int
    ) -> Dict[str, Any]:
        """
        获取知识库摘要信息
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            
        Returns:
            知识库摘要信息
        """
        kb = self.validate_knowledge_base_access(db, knowledge_base_id)
        
        # 获取ChromaDB集合统计
        collection_stats = chroma_manager.get_collection_stats(kb.collection_name)
        
        # 获取数据库统计
        from app.crud.crud_knowledge_base import document, document_chunk
        doc_stats = document.get_stats_by_kb(db, kb_id=knowledge_base_id)
        chunk_stats = document_chunk.get_stats_by_kb(db, kb_id=knowledge_base_id)
        
        return {
            "knowledge_base": {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "embedding_model": kb.embedding_model,
                "chunk_size": kb.chunk_size,
                "chunk_overlap": kb.chunk_overlap,
                "is_active": kb.is_active
            },
            "statistics": {
                **doc_stats,
                **chunk_stats,
                "vector_count": collection_stats.get("count", 0) if collection_stats else 0
            }
        }


# 创建全局RAG服务实例
rag_service = RAGService()
