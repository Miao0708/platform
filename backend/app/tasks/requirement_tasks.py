"""
需求解析相关Celery任务
"""
import os
import json
import time
import asyncio
from typing import Dict, Any
from celery import current_task
from app.core.celery_app import celery_app
from app.core.llm_client import llm_manager
from app.core.database import get_db
from app.crud.crud_task import requirement_parse_task, task_execution


@celery_app.task(bind=True)
def parse_requirement_text(self, task_id: int, config: Dict[str, Any] = None):
    """解析需求文本任务"""
    execution_id = f"exec_{self.request.id}"
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建执行记录
        execution = task_execution.create_execution(
            db=db,
            task_type="requirement_parse",
            task_id=task_id,
            steps_total=4
        )
        
        # 更新任务状态
        requirement_parse_task.update_status(
            db, task_id=task_id, status="processing"
        )
        
        # 步骤1: 获取任务信息
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=1,
            current_step="获取任务信息"
        )
        
        task = requirement_parse_task.get(db, task_id)
        if not task:
            raise Exception("任务不存在")
        
        # 步骤2: 准备内容
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=2,
            current_step="准备解析内容"
        )
        
        content = ""
        if task.input_type == "text":
            content = task.original_content or ""
        elif task.input_type == "file" and task.file_path:
            # 读取文件内容
            if os.path.exists(task.file_path):
                with open(task.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                raise Exception("文件不存在")
        
        if not content.strip():
            raise Exception("没有可解析的内容")
        
        # 步骤3: LLM解析
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=3,
            current_step="LLM解析需求"
        )
        
        # 获取LLM配置
        llm_config = config or {}
        client_type = llm_config.get("client_type", "openai")
        
        # 调用LLM解析需求
        start_time = time.time()
        llm_response = asyncio.run(llm_manager.parse_requirements(
            content=content,
            file_type=task.file_name.split('.')[-1] if task.file_name else "text",
            **llm_config
        ))
        processing_time = time.time() - start_time
        
        if not llm_response.success:
            raise Exception(f"LLM解析失败: {llm_response.error_message}")
        
        # 解析LLM返回的JSON
        try:
            parsed_data = json.loads(llm_response.content)
        except json.JSONDecodeError:
            # 如果不是有效JSON，尝试提取内容
            parsed_data = {
                "summary": llm_response.content[:500],
                "functional_requirements": [],
                "non_functional_requirements": [],
                "category": task.category,
                "priority": task.priority,
                "complexity": "medium",
                "estimated_hours": 8.0
            }
        
        # 步骤4: 保存结果
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=4,
            current_step="保存解析结果"
        )
        
        # 更新任务
        requirement_parse_task.update_status(
            db=db,
            task_id=task_id,
            status="completed",
            parsed_content=parsed_data.get("summary", ""),
            structured_requirements=parsed_data,
            category=parsed_data.get("category", task.category),
            complexity=parsed_data.get("complexity", "medium"),
            estimated_hours=parsed_data.get("estimated_hours", 8.0),
            llm_model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            processing_time=processing_time
        )
        
        # 完成执行
        task_execution.complete_execution(
            db=db,
            execution_id=execution_id,
            status="completed",
            result="需求解析完成",
            resources_used={
                "llm_model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": processing_time
            }
        )
        
        return {
            "task_id": task_id,
            "status": "completed",
            "parsed_data": parsed_data,
            "tokens_used": llm_response.tokens_used,
            "processing_time": processing_time
        }
        
    except Exception as e:
        # 任务失败
        requirement_parse_task.update_status(
            db=db,
            task_id=task_id,
            status="failed",
            error_message=str(e)
        )
        
        task_execution.complete_execution(
            db=db,
            execution_id=execution_id,
            status="failed",
            error_message=str(e)
        )
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()


@celery_app.task(bind=True)
def process_requirement_file(self, task_id: int, file_path: str, config: Dict[str, Any] = None):
    """处理需求文件任务"""
    execution_id = f"exec_{self.request.id}"
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建执行记录
        execution = task_execution.create_execution(
            db=db,
            task_type="requirement_parse",
            task_id=task_id,
            steps_total=5
        )
        
        # 更新任务状态
        requirement_parse_task.update_status(
            db, task_id=task_id, status="processing"
        )
        
        # 步骤1: 验证文件
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=1,
            current_step="验证文件"
        )
        
        if not os.path.exists(file_path):
            raise Exception("文件不存在")
        
        # 步骤2: 读取文件内容
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=2,
            current_step="读取文件内容"
        )
        
        # 根据文件类型读取内容
        file_ext = os.path.splitext(file_path)[1].lower()
        content = ""
        
        if file_ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext in ['.docx']:
            try:
                from docx import Document
                doc = Document(file_path)
                content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                raise Exception("需要安装python-docx库来处理.docx文件")
        elif file_ext in ['.pdf']:
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    content = '\n'.join([page.extract_text() for page in reader.pages])
            except ImportError:
                raise Exception("需要安装PyPDF2库来处理PDF文件")
        else:
            raise Exception(f"不支持的文件类型: {file_ext}")
        
        if not content.strip():
            raise Exception("文件内容为空")
        
        # 步骤3: 更新任务内容
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=3,
            current_step="更新任务内容"
        )
        
        task = requirement_parse_task.get(db, task_id)
        if task:
            task.original_content = content
            db.add(task)
            db.commit()
        
        # 步骤4-5: 调用文本解析任务
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=4,
            current_step="调用LLM解析"
        )
        
        # 调用文本解析任务
        result = parse_requirement_text.apply_async(
            args=[task_id, config],
            countdown=1
        )
        
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=5,
            current_step="解析完成"
        )
        
        # 完成执行
        task_execution.complete_execution(
            db=db,
            execution_id=execution_id,
            status="completed",
            result="文件处理完成，已提交解析任务"
        )
        
        return {
            "task_id": task_id,
            "status": "file_processed",
            "parse_task_id": result.id,
            "content_length": len(content)
        }
        
    except Exception as e:
        # 任务失败
        requirement_parse_task.update_status(
            db=db,
            task_id=task_id,
            status="failed",
            error_message=str(e)
        )
        
        task_execution.complete_execution(
            db=db,
            execution_id=execution_id,
            status="failed",
            error_message=str(e)
        )
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()
