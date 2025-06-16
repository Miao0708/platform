"""
文档处理服务
处理文档上传、切片、向量化等功能
"""
import os
import hashlib
import mimetypes
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader, CSVLoader
)
from app.core.config import settings
from app.core.vector_store import chroma_manager, generate_chunk_id, calculate_content_hash


class DocumentProcessor:
    """文档处理器"""
    
    # 支持的文件类型
    SUPPORTED_FILE_TYPES = {
        '.txt': 'text/plain',
        '.md': 'text/markdown', 
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.csv': 'text/csv'
    }
    
    def __init__(self):
        """初始化文档处理器"""
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    def is_supported_file_type(self, filename: str) -> bool:
        """
        检查文件类型是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            是否支持
        """
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.SUPPORTED_FILE_TYPES
    
    def get_file_type(self, filename: str) -> str:
        """
        获取文件MIME类型
        
        Args:
            filename: 文件名
            
        Returns:
            MIME类型
        """
        file_ext = Path(filename).suffix.lower()
        return self.SUPPORTED_FILE_TYPES.get(file_ext, 'application/octet-stream')
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件哈希
        
        Args:
            file_path: 文件路径
            
        Returns:
            SHA256哈希值
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def save_uploaded_file(self, file_content: bytes, filename: str, kb_id: int) -> Tuple[str, str]:
        """
        保存上传的文件
        
        Args:
            file_content: 文件内容
            filename: 原始文件名
            kb_id: 知识库ID
            
        Returns:
            (保存的文件路径, 新文件名)
        """
        # 创建知识库专用目录
        kb_dir = os.path.join(settings.UPLOAD_DIR, f"kb_{kb_id}")
        os.makedirs(kb_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = Path(filename).suffix
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        new_filename = f"{file_hash}_{filename}"
        file_path = os.path.join(kb_dir, new_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path, new_filename
    
    def load_document_content(self, file_path: str, file_type: str) -> List[str]:
        """
        加载文档内容
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            文档内容列表
        """
        try:
            if file_type == 'text/plain':
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_type == 'text/markdown':
                # 对于Markdown文件，先尝试使用unstructured，失败则使用TextLoader
                try:
                    loader = UnstructuredMarkdownLoader(file_path)
                except ImportError:
                    print("未安装unstructured库，使用TextLoader作为备用方案")
                    loader = TextLoader(file_path, encoding='utf-8')
            elif file_type == 'application/pdf':
                loader = PyPDFLoader(file_path)
            elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                # 对于Word文档，先尝试使用unstructured，失败则返回错误提示
                try:
                    loader = UnstructuredWordDocumentLoader(file_path)
                except ImportError:
                    print("未安装unstructured库，无法解析Word文档。请安装unstructured库或使用其他格式文件。")
                    return ["无法解析Word文档：缺少unstructured库。请使用文本文件(.txt)或Markdown文件(.md)代替。"]
            elif file_type == 'text/csv':
                loader = CSVLoader(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            documents = loader.load()
            return [doc.page_content for doc in documents]
        
        except Exception as e:
            print(f"加载文档失败: {e}")
            # 对于文本文件，提供最后的备用方案
            if file_type in ['text/plain', 'text/markdown']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return [content]
                except Exception as e2:
                    print(f"备用加载方案也失败: {e2}")
            return []
    
    def split_document(
        self, 
        content: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        切分文档
        
        Args:
            content: 文档内容
            chunk_size: 切片大小
            chunk_overlap: 重叠大小
            
        Returns:
            切片列表
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            
            chunks = text_splitter.split_text(content)
            return chunks
        
        except Exception as e:
            print(f"文档切分失败: {e}")
            return [content]  # 如果切分失败，返回原内容
    
    def process_document_chunks(
        self, 
        document_id: int,
        chunks: List[str],
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        处理文档切片
        
        Args:
            document_id: 文档ID
            chunks: 切片列表
            collection_name: ChromaDB集合名称
            metadata: 基础元数据
            
        Returns:
            切片信息列表
        """
        chunk_infos = []
        documents = []
        metadatas = []
        ids = []
        
        base_metadata = metadata or {}
        
        for i, chunk in enumerate(chunks):
            # 生成切片ID和哈希
            chunk_id = generate_chunk_id(document_id, i)
            content_hash = calculate_content_hash(chunk)
            
            # 准备切片元数据
            chunk_metadata = {
                **base_metadata,
                "document_id": document_id,
                "chunk_index": i,
                "chunk_id": chunk_id,
                "content_hash": content_hash
            }
            
            # 收集用于ChromaDB的数据
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)
            
            # 收集切片信息
            chunk_infos.append({
                "chunk_index": i,
                "content": chunk,
                "content_hash": content_hash,
                "embedding_id": chunk_id,
                "token_count": len(chunk.split()),  # 简单的token计数
                "chunk_metadata": chunk_metadata
            })
        
        # 批量添加到ChromaDB
        success = chroma_manager.add_documents(
            collection_name=collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        if not success:
            raise Exception("向量化存储失败")
        
        return chunk_infos
    
    def delete_document_from_vector_store(
        self, 
        document_id: int, 
        collection_name: str,
        chunk_count: int
    ) -> bool:
        """
        从向量存储中删除文档
        
        Args:
            document_id: 文档ID
            collection_name: 集合名称
            chunk_count: 切片数量
            
        Returns:
            是否删除成功
        """
        try:
            # 生成所有切片ID
            chunk_ids = [generate_chunk_id(document_id, i) for i in range(chunk_count)]
            
            # 从ChromaDB删除
            return chroma_manager.delete_documents(
                collection_name=collection_name,
                ids=chunk_ids
            )
        except Exception as e:
            print(f"从向量存储删除文档失败: {e}")
            return False


class DocumentService:
    """文档服务类"""

    def __init__(self):
        self.processor = DocumentProcessor()

    async def upload_document(
        self,
        db,
        knowledge_base_id: int,
        file,
        metadata: str = None
    ):
        """
        上传文档到知识库

        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            file: 上传的文件
            metadata: 元数据JSON字符串

        Returns:
            Document对象
        """
        from app.models.knowledge_base import Document
        from app.crud.crud_knowledge_base import knowledge_base
        import json

        # 验证知识库存在
        kb = knowledge_base.get(db, knowledge_base_id)
        if not kb:
            raise ValueError("知识库不存在")

        # 验证文件类型
        if not self.processor.is_supported_file_type(file.filename):
            raise ValueError(f"不支持的文件类型: {file.filename}")

        # 读取文件内容
        file_content = await file.read()

        # 计算文件哈希
        content_hash = hashlib.sha256(file_content).hexdigest()

        # 检查是否已存在相同文件
        from app.crud.crud_knowledge_base import document
        existing_doc = document.get_by_content_hash(db, content_hash=content_hash)
        if existing_doc:
            raise ValueError("文件已存在")

        # 保存文件
        file_path, new_filename = self.processor.save_uploaded_file(
            file_content, file.filename, knowledge_base_id
        )

        # 解析元数据
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                pass

        # 创建文档记录
        doc = Document(
            knowledge_base_id=knowledge_base_id,
            filename=new_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            file_type=self.processor.get_file_type(file.filename),
            content_hash=content_hash,
            status="pending",
            doc_metadata=doc_metadata
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        # 后台处理文档
        # TODO: 这里应该使用Celery任务
        try:
            await self.process_document(db, doc.id)
        except Exception as e:
            print(f"处理文档失败: {e}")
            document.update_status(db, document_id=doc.id, status="failed", error_message=str(e))

        return doc

    async def process_document(self, db, document_id: int):
        """
        处理文档（切片和向量化）

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        from app.crud.crud_knowledge_base import document, knowledge_base, document_chunk

        # 获取文档信息
        doc = document.get(db, document_id)
        if not doc:
            raise ValueError("文档不存在")

        # 获取知识库信息
        kb = knowledge_base.get(db, doc.knowledge_base_id)
        if not kb:
            raise ValueError("知识库不存在")

        try:
            # 更新状态为处理中
            document.update_status(db, document_id=document_id, status="processing")

            # 加载文档内容
            content_list = self.processor.load_document_content(doc.file_path, doc.file_type)
            if not content_list:
                raise Exception("无法加载文档内容")

            # 合并所有页面内容
            full_content = "\n\n".join(content_list)

            # 切分文档
            chunks = self.processor.split_document(
                full_content,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap
            )

            # 处理切片并向量化
            chunk_infos = self.processor.process_document_chunks(
                document_id=document_id,
                chunks=chunks,
                collection_name=kb.collection_name,
                metadata={
                    "filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "knowledge_base_id": kb.id
                }
            )

            # 保存切片到数据库
            chunks_data = []
            for chunk_info in chunk_infos:
                chunks_data.append({
                    "document_id": document_id,
                    **chunk_info
                })

            document_chunk.create_chunks(db, chunks_data=chunks_data)

            # 更新文档状态为完成
            document.update_status(db, document_id=document_id, status="completed")

        except Exception as e:
            # 更新状态为失败
            document.update_status(db, document_id=document_id, status="failed", error_message=str(e))
            raise


# 创建全局实例
document_processor = DocumentProcessor()
document_service = DocumentService()
