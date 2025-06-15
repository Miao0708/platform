"""
Prompt模板相关CRUD操作
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.prompt import PromptTemplate
from app.schemas.prompt import PromptTemplateCreate, PromptTemplateUpdate


class CRUDPromptTemplate(CRUDBase[PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate]):
    """Prompt模板CRUD操作"""
    
    def get_by_identifier(self, db: Session, *, identifier: str) -> Optional[PromptTemplate]:
        """根据标识符获取Prompt模板"""
        statement = select(PromptTemplate).where(PromptTemplate.identifier == identifier)
        return db.exec(statement).first()
    
    def get_by_category(self, db: Session, *, category: str) -> List[PromptTemplate]:
        """根据分类获取Prompt模板列表"""
        statement = select(PromptTemplate).where(PromptTemplate.category == category)
        return db.exec(statement).all()
    
    def get_active_templates(self, db: Session) -> List[PromptTemplate]:
        """获取所有激活的Prompt模板"""
        statement = select(PromptTemplate).where(PromptTemplate.is_active == True)
        return db.exec(statement).all()
    
    def search_by_name(self, db: Session, *, name_query: str) -> List[PromptTemplate]:
        """根据名称搜索Prompt模板"""
        statement = select(PromptTemplate).where(
            PromptTemplate.name.contains(name_query)
        )
        return db.exec(statement).all()
    
    def create(self, db: Session, *, obj_in: PromptTemplateCreate) -> PromptTemplate:
        """创建Prompt模板"""
        # 检查标识符是否已存在
        existing = self.get_by_identifier(db, identifier=obj_in.identifier)
        if existing:
            raise ValueError(f"Prompt标识符 '{obj_in.identifier}' 已存在")
        
        return super().create(db, obj_in=obj_in)
    
    def update(
        self, db: Session, *, db_obj: PromptTemplate, obj_in: PromptTemplateUpdate
    ) -> PromptTemplate:
        """更新Prompt模板"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 如果更新标识符，检查是否已存在
        if "identifier" in update_data:
            existing = self.get_by_identifier(db, identifier=update_data["identifier"])
            if existing and existing.id != db_obj.id:
                raise ValueError(f"Prompt标识符 '{update_data['identifier']}' 已存在")
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def get_categories(self, db: Session) -> List[str]:
        """获取所有分类"""
        statement = select(PromptTemplate.category).distinct()
        results = db.exec(statement).all()
        return [category for category in results if category is not None]


# 创建CRUD实例
prompt_template = CRUDPromptTemplate(PromptTemplate)
