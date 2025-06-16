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
        import uuid
        import re
        
        # 根据名称自动生成identifier
        base_identifier = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', obj_in.name.lower())
        if not base_identifier:
            base_identifier = "prompt"
        
        # 确保identifier唯一
        identifier = base_identifier
        counter = 1
        while self.get_by_identifier(db, identifier=identifier):
            identifier = f"{base_identifier}_{counter}"
            counter += 1
        
        # 创建对象时包含自动生成的identifier
        obj_data = obj_in.model_dump()
        obj_data["identifier"] = identifier
        
        from app.models.prompt import PromptTemplate
        db_obj = PromptTemplate(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
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
    
    def get_all_tags(self, db: Session) -> List[str]:
        """获取所有标签"""
        statement = select(PromptTemplate)
        prompts = db.exec(statement).all()
        
        all_tags = set()
        for prompt in prompts:
            if prompt.tags:
                all_tags.update(prompt.tags)
        
        return sorted(list(all_tags))
    
    def get_by_tags(self, db: Session, *, tags: List[str]) -> List[PromptTemplate]:
        """根据标签获取Prompt模板列表（包含任一标签的模板）"""
        if not tags:
            return []
        
        # 获取所有模板，然后在Python中过滤
        statement = select(PromptTemplate)
        all_prompts = db.exec(statement).all()
        
        filtered_prompts = []
        for prompt in all_prompts:
            if prompt.tags:
                # 检查是否有任何标签匹配
                if any(tag in prompt.tags for tag in tags):
                    filtered_prompts.append(prompt)
        
        return filtered_prompts
    
    def get_by_category_and_tags(self, db: Session, *, category: str, tags: List[str]) -> List[PromptTemplate]:
        """根据分类和标签获取Prompt模板列表"""
        if not tags:
            return self.get_by_category(db, category=category)
        
        # 先按分类筛选
        statement = select(PromptTemplate).where(PromptTemplate.category == category)
        category_prompts = db.exec(statement).all()
        
        # 再按标签筛选
        filtered_prompts = []
        for prompt in category_prompts:
            if prompt.tags:
                # 检查是否有任何标签匹配
                if any(tag in prompt.tags for tag in tags):
                    filtered_prompts.append(prompt)
        
        return filtered_prompts


# 创建CRUD实例
prompt_template = CRUDPromptTemplate(PromptTemplate)
