"""
AI模型配置相关CRUD操作
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select, func
from app.crud.base import CRUDBase
from app.models.ai_model import AIModelConfig, AIModelTestResult
from app.schemas.ai_model import AIModelConfigCreate, AIModelConfigUpdate


class CRUDAIModelConfig(CRUDBase[AIModelConfig, AIModelConfigCreate, AIModelConfigUpdate]):
    """AI模型配置CRUD操作"""
    
    def get_by_provider(self, db: Session, *, provider: str) -> List[AIModelConfig]:
        """根据提供商获取模型配置"""
        statement = select(AIModelConfig).where(AIModelConfig.provider == provider)
        return db.exec(statement).all()
    
    def get_active_models(self, db: Session) -> List[AIModelConfig]:
        """获取所有激活的模型配置"""
        statement = select(AIModelConfig).where(AIModelConfig.is_active == True)
        return db.exec(statement).all()
    
    def get_default_model(self, db: Session) -> Optional[AIModelConfig]:
        """获取默认模型配置"""
        statement = select(AIModelConfig).where(
            AIModelConfig.is_default == True,
            AIModelConfig.is_active == True
        )
        return db.exec(statement).first()
    
    def set_default_model(self, db: Session, *, model_id: int) -> bool:
        """设置默认模型"""
        try:
            # 先取消所有默认设置
            statement = select(AIModelConfig).where(AIModelConfig.is_default == True)
            current_defaults = db.exec(statement).all()
            for model in current_defaults:
                model.is_default = False
                db.add(model)
            
            # 设置新的默认模型
            model = self.get(db, model_id)
            if model:
                model.is_default = True
                model.is_active = True  # 默认模型必须是激活的
                db.add(model)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
    
    def update_usage_stats(
        self, 
        db: Session, 
        *, 
        model_id: int, 
        tokens_used: int
    ) -> Optional[AIModelConfig]:
        """更新使用统计"""
        model = self.get(db, model_id)
        if model:
            model.usage_count += 1
            model.total_tokens_used += tokens_used
            model.last_used_at = datetime.utcnow().isoformat()
            db.add(model)
            db.commit()
            db.refresh(model)
        return model
    
    def get_providers(self, db: Session) -> List[str]:
        """获取所有提供商列表"""
        statement = select(AIModelConfig.provider).distinct()
        results = db.exec(statement).all()
        return [p for p in results if p is not None]
    
    def get_stats(self, db: Session) -> dict:
        """获取模型配置统计"""
        total_models = db.exec(select(func.count(AIModelConfig.id))).first()
        active_models = db.exec(
            select(func.count(AIModelConfig.id)).where(AIModelConfig.is_active == True)
        ).first()
        total_usage = db.exec(select(func.sum(AIModelConfig.usage_count))).first()
        total_tokens = db.exec(select(func.sum(AIModelConfig.total_tokens_used))).first()
        
        return {
            "total_models": total_models or 0,
            "active_models": active_models or 0,
            "total_usage": total_usage or 0,
            "total_tokens": total_tokens or 0
        }


class CRUDAIModelTestResult(CRUDBase[AIModelTestResult, dict, dict]):
    """AI模型测试结果CRUD操作"""
    
    def create_test_result(
        self,
        db: Session,
        *,
        model_config_id: int,
        test_type: str,
        success: bool,
        latency: float = None,
        error_message: str = None,
        test_prompt: str = None,
        response_content: str = None,
        tokens_used: int = None,
        test_environment: dict = None
    ) -> AIModelTestResult:
        """创建测试结果"""
        test_result = AIModelTestResult(
            model_config_id=model_config_id,
            test_type=test_type,
            success=success,
            latency=latency,
            error_message=error_message,
            test_prompt=test_prompt,
            response_content=response_content,
            tokens_used=tokens_used,
            test_environment=test_environment
        )
        
        db.add(test_result)
        db.commit()
        db.refresh(test_result)
        return test_result
    
    def get_by_model(self, db: Session, *, model_config_id: int) -> List[AIModelTestResult]:
        """获取模型的测试结果"""
        statement = select(AIModelTestResult).where(
            AIModelTestResult.model_config_id == model_config_id
        ).order_by(AIModelTestResult.created_at.desc())
        return db.exec(statement).all()
    
    def get_latest_test(
        self, 
        db: Session, 
        *, 
        model_config_id: int, 
        test_type: str = "connection"
    ) -> Optional[AIModelTestResult]:
        """获取最新的测试结果"""
        statement = select(AIModelTestResult).where(
            AIModelTestResult.model_config_id == model_config_id,
            AIModelTestResult.test_type == test_type
        ).order_by(AIModelTestResult.created_at.desc()).limit(1)
        return db.exec(statement).first()
    
    def get_success_rate(self, db: Session, *, model_config_id: int) -> float:
        """获取模型的成功率"""
        total_tests = db.exec(
            select(func.count(AIModelTestResult.id)).where(
                AIModelTestResult.model_config_id == model_config_id
            )
        ).first()
        
        successful_tests = db.exec(
            select(func.count(AIModelTestResult.id)).where(
                AIModelTestResult.model_config_id == model_config_id,
                AIModelTestResult.success == True
            )
        ).first()
        
        if total_tests and total_tests > 0:
            return (successful_tests or 0) / total_tests * 100
        return 0.0
    
    def get_avg_latency(self, db: Session, *, model_config_id: int) -> Optional[float]:
        """获取平均延迟"""
        avg_latency = db.exec(
            select(func.avg(AIModelTestResult.latency)).where(
                AIModelTestResult.model_config_id == model_config_id,
                AIModelTestResult.success == True,
                AIModelTestResult.latency.is_not(None)
            )
        ).first()
        return avg_latency


# 创建CRUD实例
ai_model_config = CRUDAIModelConfig(AIModelConfig)
ai_model_test_result = CRUDAIModelTestResult(AIModelTestResult)
