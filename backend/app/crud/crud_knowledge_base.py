"""
知识库相关CRUD操作
"""
import os
from typing import Optional, List
from sqlmodel import Session, select, func
from app.crud.base import CRUDBase
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
from app.core.vector_store import chroma_manager


class CRUDKnowledgeBase(CRUDBase[KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate]):
    """知识库CRUD操作"""
    
    def create(self, db: Session, *, obj_in: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库"""
        # 生成唯一的集合名称
        collection_name = f"kb_{obj_in.name.lower().replace(' ', '_')}_{hash(obj_in.name) % 10000}"
        
        # 创建数据库记录
        db_obj = KnowledgeBase(
            name=obj_in.name,
            description=obj_in.description,
            collection_name=collection_name,
            embedding_model=obj_in.embedding_model,
            chunk_size=obj_in.chunk_size,
            chunk_overlap=obj_in.chunk_overlap
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 创建ChromaDB集合
        metadata = {
            "knowledge_base_id": db_obj.id,
            "embedding_model": obj_in.embedding_model,
            "chunk_size": obj_in.chunk_size,
            "chunk_overlap": obj_in.chunk_overlap
        }
        
        success = chroma_manager.create_collection(
            collection_name=collection_name,
            metadata=metadata
        )
        
        if not success:
            # 如果ChromaDB集合创建失败，删除数据库记录
            db.delete(db_obj)
            db.commit()
            raise Exception("创建向量存储集合失败")
        
        return db_obj
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[KnowledgeBase]:
        """根据名称获取知识库"""
        statement = select(KnowledgeBase).where(KnowledgeBase.name == name)
        return db.exec(statement).first()
    
    def get_active_knowledge_bases(self, db: Session) -> List[KnowledgeBase]:
        """获取所有激活的知识库"""
        statement = select(KnowledgeBase).where(KnowledgeBase.is_active == True)
        return db.exec(statement).all()
    
    def remove(self, db: Session, *, id: int) -> KnowledgeBase:
        """删除知识库"""
        kb = self.get(db, id)
        if not kb:
            raise ValueError("知识库不存在")
        
        # 删除ChromaDB集合
        chroma_manager.delete_collection(kb.collection_name)
        
        # 删除相关文档文件
        try:
            import shutil
            kb_dir = os.path.join("uploads", f"kb_{id}")
            if os.path.exists(kb_dir):
                shutil.rmtree(kb_dir)
        except Exception as e:
            print(f"删除文件目录失败: {e}")
        
        # 删除数据库记录（级联删除文档和切片）
        db.delete(kb)
        db.commit()
        return kb


class CRUDDocument(CRUDBase[Document, dict, dict]):
    """文档CRUD操作"""
    
    def get_by_knowledge_base(self, db: Session, *, kb_id: int) -> List[Document]:
        """获取知识库下的所有文档"""
        statement = select(Document).where(Document.knowledge_base_id == kb_id)
        return db.exec(statement).all()
    
    def get_by_content_hash(self, db: Session, *, content_hash: str) -> Optional[Document]:
        """根据内容哈希获取文档"""
        statement = select(Document).where(Document.content_hash == content_hash)
        return db.exec(statement).first()
    
    def get_by_status(self, db: Session, *, status: str) -> List[Document]:
        """根据状态获取文档"""
        statement = select(Document).where(Document.status == status)
        return db.exec(statement).all()
    
    def update_status(
        self, db: Session, *, document_id: int, status: str, error_message: str = None
    ) -> Optional[Document]:
        """更新文档状态"""
        document = self.get(db, document_id)
        if document:
            document.status = status
            if error_message:
                document.error_message = error_message
            db.add(document)
            db.commit()
            db.refresh(document)
        return document
    
    def get_stats_by_kb(self, db: Session, *, kb_id: int) -> dict:
        """获取知识库文档统计"""
        # 总文档数
        total_docs = db.exec(
            select(func.count(Document.id)).where(Document.knowledge_base_id == kb_id)
        ).first()
        
        # 处理中的文档数
        processing_docs = db.exec(
            select(func.count(Document.id)).where(
                Document.knowledge_base_id == kb_id,
                Document.status.in_(["pending", "processing"])
            )
        ).first()
        
        # 失败的文档数
        failed_docs = db.exec(
            select(func.count(Document.id)).where(
                Document.knowledge_base_id == kb_id,
                Document.status == "failed"
            )
        ).first()
        
        # 总文件大小
        total_size = db.exec(
            select(func.sum(Document.file_size)).where(Document.knowledge_base_id == kb_id)
        ).first() or 0
        
        return {
            "total_documents": total_docs or 0,
            "processing_documents": processing_docs or 0,
            "failed_documents": failed_docs or 0,
            "total_size": total_size
        }


class CRUDDocumentChunk(CRUDBase[DocumentChunk, dict, dict]):
    """文档切片CRUD操作"""
    
    def get_by_document(self, db: Session, *, document_id: int) -> List[DocumentChunk]:
        """获取文档的所有切片"""
        statement = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index)
        return db.exec(statement).all()
    
    def get_by_embedding_id(self, db: Session, *, embedding_id: str) -> Optional[DocumentChunk]:
        """根据嵌入ID获取切片"""
        statement = select(DocumentChunk).where(DocumentChunk.embedding_id == embedding_id)
        return db.exec(statement).first()
    
    def create_chunks(self, db: Session, *, chunks_data: List[dict]) -> List[DocumentChunk]:
        """批量创建文档切片"""
        chunks = []
        for chunk_data in chunks_data:
            chunk = DocumentChunk(**chunk_data)
            db.add(chunk)
            chunks.append(chunk)
        
        db.commit()
        for chunk in chunks:
            db.refresh(chunk)
        
        return chunks
    
    def delete_by_document(self, db: Session, *, document_id: int) -> int:
        """删除文档的所有切片"""
        statement = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        chunks = db.exec(statement).all()
        
        count = len(chunks)
        for chunk in chunks:
            db.delete(chunk)
        
        db.commit()
        return count
    
    def get_stats_by_kb(self, db: Session, *, kb_id: int) -> dict:
        """获取知识库切片统计"""
        # 通过JOIN查询获取知识库的切片统计
        total_chunks = db.exec(
            select(func.count(DocumentChunk.id))
            .select_from(DocumentChunk)
            .join(Document)
            .where(Document.knowledge_base_id == kb_id)
        ).first()
        
        return {
            "total_chunks": total_chunks or 0
        }


# 创建CRUD实例
knowledge_base = CRUDKnowledgeBase(KnowledgeBase)
document = CRUDDocument(Document)
document_chunk = CRUDDocumentChunk(DocumentChunk)
