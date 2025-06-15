"""
ChromaDB向量存储封装
"""
import os
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from app.core.config import settings


class ChromaDBManager:
    """ChromaDB管理器"""
    
    def __init__(self):
        """初始化ChromaDB客户端"""
        # 确保持久化目录存在
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        # 创建持久化客户端
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def create_collection(self, collection_name: str, metadata: Optional[Dict] = None) -> bool:
        """
        创建集合
        
        Args:
            collection_name: 集合名称
            metadata: 集合元数据
            
        Returns:
            是否创建成功
        """
        try:
            # 检查集合是否已存在
            existing_collections = [col.name for col in self.client.list_collections()]
            if collection_name in existing_collections:
                return False
            
            # 创建集合
            self.client.create_collection(
                name=collection_name,
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            print(f"创建集合失败: {e}")
            return False
    
    def get_collection(self, collection_name: str):
        """
        获取集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            ChromaDB集合对象
        """
        try:
            return self.client.get_collection(name=collection_name)
        except Exception as e:
            print(f"获取集合失败: {e}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否删除成功
        """
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            print(f"删除集合失败: {e}")
            return False
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str]
    ) -> bool:
        """
        添加文档到集合
        
        Args:
            collection_name: 集合名称
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Returns:
            是否添加成功
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return False
            
            # 批量添加文档
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def search_documents(
        self, 
        collection_name: str, 
        query_texts: List[str], 
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        搜索文档
        
        Args:
            collection_name: 集合名称
            query_texts: 查询文本列表
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件
            
        Returns:
            搜索结果
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return None
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            print(f"搜索文档失败: {e}")
            return None
    
    def update_documents(
        self, 
        collection_name: str, 
        ids: List[str], 
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        更新文档
        
        Args:
            collection_name: 集合名称
            ids: 文档ID列表
            documents: 新的文档内容列表
            metadatas: 新的元数据列表
            
        Returns:
            是否更新成功
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return False
            
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"更新文档失败: {e}")
            return False
    
    def delete_documents(self, collection_name: str, ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            collection_name: 集合名称
            ids: 要删除的文档ID列表
            
        Returns:
            是否删除成功
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return False
            
            collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def get_collection_stats(self, collection_name: str) -> Optional[Dict]:
        """
        获取集合统计信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            统计信息字典
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return None
            
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            print(f"获取集合统计失败: {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            集合名称列表
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"列出集合失败: {e}")
            return []


def generate_chunk_id(document_id: int, chunk_index: int) -> str:
    """
    生成切片ID
    
    Args:
        document_id: 文档ID
        chunk_index: 切片索引
        
    Returns:
        切片ID
    """
    return f"doc_{document_id}_chunk_{chunk_index}"


def calculate_content_hash(content: str) -> str:
    """
    计算内容哈希
    
    Args:
        content: 内容字符串
        
    Returns:
        SHA256哈希值
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


# 创建全局ChromaDB管理器实例
chroma_manager = ChromaDBManager()
