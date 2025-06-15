"""
流水线执行相关Celery任务
"""
import os
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any
from celery import current_task
from app.core.celery_app import celery_app
from app.core.llm_client import llm_manager
from app.core.database import get_db
from app.crud.crud_task import pipeline_task, code_diff_task, requirement_parse_task, task_execution
from app.crud.crud_prompt import prompt_template
from app.crud.crud_knowledge_base import knowledge_base
from app.services.rag_service import rag_service


@celery_app.task(bind=True)
def execute_pipeline(self, task_id: int, config_override: Dict[str, Any] = None):
    """执行流水线任务"""
    execution_id = f"exec_{self.request.id}"
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建执行记录
        execution = task_execution.create_execution(
            db=db,
            task_type="pipeline",
            task_id=task_id,
            steps_total=5
        )
        
        # 更新任务状态
        pipeline_task.update_status(
            db, task_id=task_id, 
            status="running",
            started_at=datetime.utcnow().isoformat()
        )
        
        # 步骤1: 获取任务信息
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=1,
            current_step="获取任务信息"
        )
        
        task = pipeline_task.get(db, task_id)
        if not task:
            raise Exception("流水线任务不存在")
        
        # 步骤2: 收集输入数据
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=2,
            current_step="收集输入数据"
        )
        
        # 获取代码差异内容
        code_diff_content = ""
        code_diff_summary = ""
        if task.code_diff_task_id:
            code_task = code_diff_task.get(db, task.code_diff_task_id)
            if code_task and code_task.diff_file_path and os.path.exists(code_task.diff_file_path):
                with open(code_task.diff_file_path, 'r', encoding='utf-8') as f:
                    code_diff_content = f.read()
                code_diff_summary = code_task.diff_summary or ""
        
        # 获取需求内容
        requirement_content = ""
        structured_requirements = {}
        if task.requirement_task_id:
            req_task = requirement_parse_task.get(db, task.requirement_task_id)
            if req_task:
                requirement_content = req_task.parsed_content or req_task.original_content or ""
                structured_requirements = req_task.structured_requirements or {}
        
        # 步骤3: 获取知识库上下文
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=3,
            current_step="获取知识库上下文"
        )
        
        knowledge_context = ""
        if task.knowledge_base_id and (code_diff_content or requirement_content):
            try:
                # 构建查询内容
                query_content = ""
                if code_diff_content:
                    query_content += f"代码变更: {code_diff_content[:1000]}\n"
                if requirement_content:
                    query_content += f"需求内容: {requirement_content[:1000]}"
                
                if query_content.strip():
                    context, _ = rag_service.get_context_for_query(
                        db,
                        query=query_content,
                        knowledge_base_id=task.knowledge_base_id,
                        max_context_length=2000
                    )
                    knowledge_context = context
            except Exception as e:
                print(f"获取知识库上下文失败: {e}")
        
        # 步骤4: 构建Prompt
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=4,
            current_step="构建执行Prompt"
        )
        
        final_prompt = ""
        if task.prompt_template_id:
            template = prompt_template.get(db, task.prompt_template_id)
            if template:
                from app.services.prompt_service import prompt_service
                
                variables = {
                    "code_diff": code_diff_content,
                    "code_diff_summary": code_diff_summary,
                    "requirement_content": requirement_content,
                    "structured_requirements": json.dumps(structured_requirements, ensure_ascii=False, indent=2),
                    "knowledge_context": knowledge_context,
                    "pipeline_type": task.pipeline_type,
                    "task_name": task.name,
                    "task_description": task.description or ""
                }
                
                final_prompt = await prompt_service.resolve_prompt_content(
                    db, template.content, variables
                )
        
        # 如果没有模板，使用默认prompt
        if not final_prompt:
            final_prompt = build_default_prompt(
                task.pipeline_type,
                code_diff_content,
                requirement_content,
                knowledge_context
            )
        
        # 步骤5: 执行LLM任务
        task_execution.update_progress(
            db, execution_id=execution_id,
            steps_completed=5,
            current_step="执行LLM任务"
        )
        
        # 合并配置
        llm_config = task.config or {}
        if config_override:
            llm_config.update(config_override)
        
        # 调用LLM
        start_time = time.time()
        
        if task.pipeline_type == "code_review":
            llm_response = asyncio.run(llm_manager.review_code(
                code_diff=code_diff_content,
                requirements=requirement_content,
                focus_areas=llm_config.get("focus_areas", ["security", "quality"]),
                **llm_config
            ))
        else:
            # 通用文本完成
            llm_response = asyncio.run(llm_manager.text_completion(
                prompt=final_prompt,
                **llm_config
            ))
        
        execution_time = time.time() - start_time
        
        if not llm_response.success:
            raise Exception(f"LLM执行失败: {llm_response.error_message}")
        
        # 解析结果
        result_data = {}
        try:
            if task.pipeline_type == "code_review":
                result_data = json.loads(llm_response.content)
            else:
                result_data = {"content": llm_response.content}
        except json.JSONDecodeError:
            result_data = {"content": llm_response.content}
        
        # 完成任务
        pipeline_task.update_status(
            db=db,
            task_id=task_id,
            status="completed",
            result=llm_response.content,
            result_data=result_data,
            completed_at=datetime.utcnow().isoformat(),
            execution_time=execution_time,
            llm_model=llm_response.model,
            tokens_used=llm_response.tokens_used
        )
        
        # 完成执行
        task_execution.complete_execution(
            db=db,
            execution_id=execution_id,
            status="completed",
            result="流水线执行完成",
            resources_used={
                "llm_model": llm_response.model,
                "tokens_used": llm_response.tokens_used,
                "processing_time": execution_time
            }
        )
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result_data": result_data,
            "tokens_used": llm_response.tokens_used,
            "execution_time": execution_time
        }
        
    except Exception as e:
        # 任务失败
        pipeline_task.update_status(
            db=db,
            task_id=task_id,
            status="failed",
            error_message=str(e),
            completed_at=datetime.utcnow().isoformat()
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


def build_default_prompt(
    pipeline_type: str,
    code_diff: str,
    requirement: str,
    knowledge_context: str
) -> str:
    """构建默认的流水线prompt"""
    
    if pipeline_type == "code_review":
        prompt = f"""
请对以下代码变更进行详细评审：

{'相关需求：' + requirement if requirement else ''}

代码差异：
{code_diff}

{'相关知识：' + knowledge_context if knowledge_context else ''}

请按照以下JSON格式返回评审结果：
{{
    "summary": "评审摘要",
    "issues": [
        {{
            "type": "问题类型",
            "severity": "严重程度",
            "description": "问题描述",
            "suggestion": "修改建议"
        }}
    ],
    "suggestions": ["改进建议"],
    "security_score": 安全评分,
    "quality_score": 质量评分
}}
"""
    
    elif pipeline_type == "test_generation":
        prompt = f"""
基于以下信息生成测试用例：

{'需求内容：' + requirement if requirement else ''}

{'代码变更：' + code_diff if code_diff else ''}

{'相关知识：' + knowledge_context if knowledge_context else ''}

请生成详细的测试用例，包括单元测试、集成测试和端到端测试。
"""
    
    elif pipeline_type == "documentation":
        prompt = f"""
基于以下信息生成技术文档：

{'需求内容：' + requirement if requirement else ''}

{'代码变更：' + code_diff if code_diff else ''}

{'相关知识：' + knowledge_context if knowledge_context else ''}

请生成清晰、详细的技术文档，包括功能说明、使用方法和注意事项。
"""
    
    else:
        prompt = f"""
请分析以下内容：

{'需求内容：' + requirement if requirement else ''}

{'代码变更：' + code_diff if code_diff else ''}

{'相关知识：' + knowledge_context if knowledge_context else ''}

请提供详细的分析和建议。
"""
    
    return prompt
