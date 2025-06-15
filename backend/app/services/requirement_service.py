"""
需求管理后台任务服务
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Session

from app.core.database import engine
from app.crud.crud_requirement import requirement_document, requirement_analysis_task, requirement_test_task
from app.crud.crud_prompt import prompt_template
from app.crud.crud_ai_model import ai_model_config
from app.services.ai_service import AIService
from app.utils.file_processor import extract_file_content
import logging

logger = logging.getLogger(__name__)


class RequirementBackgroundTaskService:
    """需求管理后台任务服务"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.running_tasks = {}  # 存储正在运行的任务
    
    async def process_requirement_analysis(self, task_id: int) -> None:
        """处理需求分析任务"""
        with Session(engine) as db:
            try:
                # 获取任务信息
                task = requirement_analysis_task.get(db, id=task_id)
                if not task:
                    logger.error(f"需求分析任务 {task_id} 不存在")
                    return
                
                # 更新任务状态为运行中
                requirement_analysis_task.update_status(
                    db, task_id=task_id, status="running"
                )
                
                # 获取需求文档
                requirement_doc = requirement_document.get(db, id=task.requirement_document_id)
                if not requirement_doc:
                    requirement_analysis_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="关联的需求文档不存在"
                    )
                    return
                
                # 获取Prompt模板
                prompt = prompt_template.get(db, id=task.prompt_template_id)
                if not prompt:
                    requirement_analysis_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="Prompt模板不存在"
                    )
                    return
                
                # 获取AI模型配置
                model_config = ai_model_config.get(db, id=task.model_config_id)
                if not model_config:
                    requirement_analysis_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="AI模型配置不存在"
                    )
                    return
                
                # 构建分析内容（使用优化后的内容，如果没有则使用原始内容）
                content_to_analyze = requirement_doc.optimized_content or requirement_doc.original_content
                
                # 准备Prompt
                prompt_text = prompt.content
                # 如果prompt包含变量，进行替换
                if "{requirement_content}" in prompt_text:
                    prompt_text = prompt_text.replace("{requirement_content}", content_to_analyze)
                
                # 执行AI分析
                start_time = time.time()
                success, result, tokens_used, error_msg = await self.ai_service.generate_text(
                    prompt=prompt_text,
                    model_config=model_config.to_dict()
                )
                execution_time = time.time() - start_time
                
                if success:
                    # 更新任务为成功状态
                    requirement_analysis_task.update_status(
                        db, task_id=task_id, status="completed",
                        result=result, tokens_used=tokens_used, 
                        execution_time=execution_time
                    )
                    
                    # 如果这是需求优化任务，更新需求文档的优化内容
                    if "优化" in prompt.name or "optimize" in prompt.name.lower():
                        requirement_document.set_optimized_content(
                            db, requirement_id=requirement_doc.id, 
                            optimized_content=result
                        )
                        requirement_document.update_status(
                            db, requirement_id=requirement_doc.id, status="completed"
                        )
                else:
                    # 更新任务为失败状态
                    requirement_analysis_task.update_status(
                        db, task_id=task_id, status="failed",
                        error_message=error_msg, execution_time=execution_time
                    )
                    
            except Exception as e:
                logger.error(f"处理需求分析任务 {task_id} 时出错: {str(e)}")
                requirement_analysis_task.update_status(
                    db, task_id=task_id, status="failed",
                    error_message=f"任务执行异常: {str(e)}"
                )
    
    async def process_requirement_test_analysis(self, task_id: int) -> None:
        """处理需求测试分析任务"""
        with Session(engine) as db:
            try:
                # 获取任务信息
                task = requirement_test_task.get(db, id=task_id)
                if not task:
                    logger.error(f"需求测试分析任务 {task_id} 不存在")
                    return
                
                # 更新任务状态为运行中
                requirement_test_task.update_status(
                    db, task_id=task_id, status="running"
                )
                
                # 获取需求内容
                if task.requirement_id:
                    # 使用关联的需求文档
                    requirement_doc = requirement_document.get(db, id=task.requirement_id)
                    if not requirement_doc:
                        requirement_test_task.update_status(
                            db, task_id=task_id, status="failed", 
                            error_message="关联的需求文档不存在"
                        )
                        return
                    content_to_analyze = requirement_doc.optimized_content or requirement_doc.original_content
                else:
                    # 使用直接输入的内容
                    content_to_analyze = task.requirement_content
                
                if not content_to_analyze:
                    requirement_test_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="没有找到需要分析的需求内容"
                    )
                    return
                
                # 获取Prompt模板
                prompt = prompt_template.get(db, id=task.prompt_template_id)
                if not prompt:
                    requirement_test_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="Prompt模板不存在"
                    )
                    return
                
                # 获取AI模型配置
                model_config = ai_model_config.get(db, id=task.model_config_id)
                if not model_config:
                    requirement_test_task.update_status(
                        db, task_id=task_id, status="failed", 
                        error_message="AI模型配置不存在"
                    )
                    return
                
                # 准备Prompt
                prompt_text = prompt.content
                if "{requirement_content}" in prompt_text:
                    prompt_text = prompt_text.replace("{requirement_content}", content_to_analyze)
                
                # 执行AI测试分析
                start_time = time.time()
                success, result, tokens_used, error_msg = await self.ai_service.generate_text(
                    prompt=prompt_text,
                    model_config=model_config.to_dict()
                )
                execution_time = time.time() - start_time
                
                if success:
                    # 尝试解析结果为JSON格式
                    try:
                        parsed_result = json.loads(result) if result.startswith('{') else {"analysis": result}
                    except json.JSONDecodeError:
                        parsed_result = {"analysis": result}
                    
                    # 更新任务为成功状态
                    requirement_test_task.update_status(
                        db, task_id=task_id, status="completed",
                        result=parsed_result, tokens_used=tokens_used, 
                        execution_time=execution_time
                    )
                else:
                    # 更新任务为失败状态
                    requirement_test_task.update_status(
                        db, task_id=task_id, status="failed",
                        error_message=error_msg, execution_time=execution_time
                    )
                    
            except Exception as e:
                logger.error(f"处理需求测试分析任务 {task_id} 时出错: {str(e)}")
                requirement_test_task.update_status(
                    db, task_id=task_id, status="failed",
                    error_message=f"任务执行异常: {str(e)}"
                )
    
    async def process_file_upload(self, requirement_id: int, file_path: str) -> None:
        """处理文件上传和内容提取"""
        with Session(engine) as db:
            try:
                # 获取需求文档
                requirement_doc = requirement_document.get(db, id=requirement_id)
                if not requirement_doc:
                    logger.error(f"需求文档 {requirement_id} 不存在")
                    return
                
                # 更新状态为处理中
                requirement_document.update_status(
                    db, requirement_id=requirement_id, status="processing"
                )
                
                # 提取文件内容
                success, content, error_msg = extract_file_content(file_path)
                
                if success and content:
                    # 更新需求文档内容
                    requirement_document.update(
                        db, db_obj=requirement_doc, 
                        obj_in={"original_content": content}
                    )
                    
                    # 如果有配置的prompt和模型，自动开始分析任务
                    if requirement_doc.prompt_template_id and requirement_doc.model_config_id:
                        # 创建分析任务
                        from app.schemas.requirement import RequirementAnalysisTaskCreate
                        task_data = RequirementAnalysisTaskCreate(
                            requirement_document_id=requirement_id,
                            prompt_template_id=requirement_doc.prompt_template_id,
                            model_config_id=requirement_doc.model_config_id
                        )
                        analysis_task = requirement_analysis_task.create(db, obj_in=task_data)
                        
                        # 启动分析任务
                        asyncio.create_task(self.process_requirement_analysis(analysis_task.id))
                    else:
                        # 只是标记为已完成文件处理
                        requirement_document.update_status(
                            db, requirement_id=requirement_id, status="pending"
                        )
                else:
                    # 文件处理失败
                    requirement_document.update_status(
                        db, requirement_id=requirement_id, status="failed",
                        error_message=error_msg or "文件内容提取失败"
                    )
                    
            except Exception as e:
                logger.error(f"处理文件上传任务 {requirement_id} 时出错: {str(e)}")
                requirement_document.update_status(
                    db, requirement_id=requirement_id, status="failed",
                    error_message=f"文件处理异常: {str(e)}"
                )
    
    def start_requirement_analysis_task(self, task_id: int) -> None:
        """启动需求分析任务（同步接口）"""
        if task_id in self.running_tasks:
            logger.warning(f"需求分析任务 {task_id} 已在运行中")
            return
        
        # 记录任务
        self.running_tasks[task_id] = "requirement_analysis"
        
        # 启动异步任务
        async def run_task():
            try:
                await self.process_requirement_analysis(task_id)
            finally:
                self.running_tasks.pop(task_id, None)
        
        asyncio.create_task(run_task())
    
    def start_requirement_test_task(self, task_id: int) -> None:
        """启动需求测试分析任务（同步接口）"""
        if task_id in self.running_tasks:
            logger.warning(f"需求测试分析任务 {task_id} 已在运行中")
            return
        
        # 记录任务
        self.running_tasks[task_id] = "requirement_test"
        
        # 启动异步任务
        async def run_task():
            try:
                await self.process_requirement_test_analysis(task_id)
            finally:
                self.running_tasks.pop(task_id, None)
        
        asyncio.create_task(run_task())
    
    def start_file_processing_task(self, requirement_id: int, file_path: str) -> None:
        """启动文件处理任务（同步接口）"""
        task_key = f"file_{requirement_id}"
        if task_key in self.running_tasks:
            logger.warning(f"文件处理任务 {requirement_id} 已在运行中")
            return
        
        # 记录任务
        self.running_tasks[task_key] = "file_processing"
        
        # 启动异步任务
        async def run_task():
            try:
                await self.process_file_upload(requirement_id, file_path)
            finally:
                self.running_tasks.pop(task_key, None)
        
        asyncio.create_task(run_task())


# 全局任务服务实例
requirement_task_service = RequirementBackgroundTaskService() 