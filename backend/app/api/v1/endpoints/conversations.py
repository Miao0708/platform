"""
AI对话功能API端点（适配前端需求）
"""
import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import json
import asyncio
import time
from datetime import datetime
from app.api.v1.deps import get_db
from app.models.conversation import Conversation, Message
from app.models.ai_model import AIModelConfig
from app.schemas.ai_model import (
    ConversationCreate, ConversationUpdate, ConversationResponse, 
    ConversationDetailResponse, MessageCreate, MessageResponse
)
from app.core.response import StandardJSONResponse
from app.core.llm_client import llm_manager
from app.crud.crud_ai_model import ai_model_config

router = APIRouter()


@router.get("/conversations", tags=["AI对话"])
def get_conversations(
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """获取对话列表"""
    try:
        statement = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.is_active == True
        ).order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
        
        conversations = db.exec(statement).all()
        
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": str(conv.id),
                "title": conv.title,
                "model_config_id": str(conv.model_config_id),
                "total_tokens": conv.total_tokens,
                "message_count": conv.message_count,
                "last_message_at": conv.last_message_at,
    
                "is_pinned": conv.is_pinned
            })
        
        return StandardJSONResponse(
            content=conversation_list,
            message="获取对话列表成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取对话列表失败: {str(e)}"
        )


@router.post("/conversations", tags=["AI对话"])
def create_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_in: ConversationCreate,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """创建新对话"""
    try:
        # 验证AI模型配置存在
        model = ai_model_config.get(db=db, id=int(conversation_in.model_config_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        # 创建对话
        conversation = Conversation(
            user_id=user_id,
            title=conversation_in.title,
            model_config_id=int(conversation_in.model_config_id)
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return StandardJSONResponse(
            content={
                "id": str(conversation.id),
                "title": conversation.title,
                "model_config_id": str(conversation.model_config_id),
                "total_tokens": conversation.total_tokens,
                "message_count": conversation.message_count,
    
            },
            message="对话创建成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"创建对话失败: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", tags=["AI对话"])
def get_conversation_detail(
    *,
    db: Session = Depends(get_db),
    conversation_id: str,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """获取对话详情"""
    try:
        # 获取对话
        conversation = db.exec(
            select(Conversation).where(
                Conversation.id == int(conversation_id),
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="对话不存在"
            )
        
        # 获取消息列表
        messages = db.exec(
            select(Message).where(
                Message.conversation_id == int(conversation_id)
            ).order_by(Message.created_at.asc())
        ).all()
        
        message_list = []
        for msg in messages:
            message_list.append({
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": "2024-01-01T00:00:00Z",
                "tokens": msg.tokens
            })
        
        conversation_detail = {
            "id": str(conversation.id),
            "title": conversation.title,
            "model_config_id": str(conversation.model_config_id),
            "messages": message_list,
            "total_tokens": conversation.total_tokens
        }
        
        return StandardJSONResponse(
            content=conversation_detail,
            message="获取对话详情成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取对话详情失败: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages", tags=["AI对话"])
async def send_message(
    *,
    db: Session = Depends(get_db),
    conversation_id: str,
    message_in: MessageCreate,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """发送消息"""
    try:
        # 获取对话
        conversation = db.exec(
            select(Conversation).where(
                Conversation.id == int(conversation_id),
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="对话不存在"
            )
        
        # 获取AI模型配置
        model_config_id = message_in.model_config_id or str(conversation.model_config_id)
        model = ai_model_config.get(db=db, id=int(model_config_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        # 保存用户消息
        user_message = Message(
            conversation_id=int(conversation_id),
            role="user",
            content=message_in.content,
            context_data=message_in.context
        )
        db.add(user_message)
        
        # 获取对话历史
        history_messages = db.exec(
            select(Message).where(
                Message.conversation_id == int(conversation_id)
            ).order_by(Message.created_at.asc())
        ).all()
        
        # 构建消息历史
        messages = []
        if conversation.system_prompt:
            messages.append({"role": "system", "content": conversation.system_prompt})
        
        for msg in history_messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": message_in.content})
        
        # 调用LLM
        start_time = time.time()
        
        llm_config = {
            "api_key": model.api_key,
            "base_url": model.base_url,
            "model": model.model,
            "temperature": model.temperature,
            "max_tokens": model.max_tokens,
            "timeout": model.timeout
        }
        
        llm_response = await llm_manager.chat_completion(
            messages=messages,
            **llm_config
        )
        
        processing_time = time.time() - start_time
        
        if not llm_response.success:
            # 保存错误消息
            error_message = Message(
                conversation_id=int(conversation_id),
                role="assistant",
                content="抱歉，我遇到了一些问题，请稍后再试。",
                error_message=llm_response.error_message,
                processing_time=processing_time
            )
            db.add(error_message)
            db.commit()
            
            return StandardJSONResponse(
                content=None,
                status_code=500,
                message=f"AI响应失败: {llm_response.error_message}"
            )
        
        # 保存AI响应
        ai_message = Message(
            conversation_id=int(conversation_id),
            role="assistant",
            content=llm_response.content,
            tokens=llm_response.tokens_used,
            model_used=llm_response.model,
            processing_time=processing_time,
            prompt_template_id=int(message_in.prompt_template_id) if message_in.prompt_template_id else None
        )
        db.add(ai_message)
        
        # 更新对话统计
        conversation.total_tokens += llm_response.tokens_used
        conversation.message_count += 2  # 用户消息 + AI消息
        conversation.last_message_at = datetime.utcnow().isoformat()
        db.add(conversation)
        
        # 更新模型使用统计
        ai_model_config.update_usage_stats(
            db, model_id=int(model_config_id), tokens_used=llm_response.tokens_used
        )
        
        db.commit()
        db.refresh(ai_message)
        
        return StandardJSONResponse(
            content={
                "id": str(ai_message.id),
                "role": ai_message.role,
                "content": ai_message.content,
                "timestamp": "2024-01-01T00:00:00Z",
                "tokens": ai_message.tokens
            },
            message="消息发送成功"
        )
    except Exception as e:
        db.rollback()
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"发送消息失败: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages/stream", tags=["AI对话"])
async def send_message_stream(
    *,
    db: Session = Depends(get_db),
    conversation_id: str,
    message_in: MessageCreate,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """发送流式消息（SSE）"""
    
    async def event_stream():
        try:
            # 获取对话
            conversation = db.exec(
                select(Conversation).where(
                    Conversation.id == int(conversation_id),
                    Conversation.user_id == user_id
                )
            ).first()
            
            if not conversation:
                yield f"data: {json.dumps({'type': 'error', 'content': '对话不存在'})}\n\n"
                return
            
            # 获取AI模型配置
            model_config_id = message_in.model_config_id or str(conversation.model_config_id)
            model = ai_model_config.get(db=db, id=int(model_config_id))
            if not model:
                yield f"data: {json.dumps({'type': 'error', 'content': 'AI模型配置不存在'})}\n\n"
                return
            
            # 保存用户消息
            user_message = Message(
                conversation_id=int(conversation_id),
                role="user",
                content=message_in.content,
                context_data=message_in.context
            )
            db.add(user_message)
            db.commit()
            
            # 获取对话历史
            history_messages = db.exec(
                select(Message).where(
                    Message.conversation_id == int(conversation_id)
                ).order_by(Message.created_at.asc())
            ).all()
            
            # 构建消息历史
            messages = []
            if conversation.system_prompt:
                messages.append({"role": "system", "content": conversation.system_prompt})
            
            for msg in history_messages:
                messages.append({"role": msg.role, "content": msg.content})
            
            # 准备流式响应
            yield f"data: {json.dumps({'type': 'start', 'content': '开始生成回复...'})}\n\n"
            
            # 调用LLM流式接口
            full_response = ""
            start_time = time.time()
            
            try:
                # 这里需要实现LLM的流式调用
                # 模拟流式响应
                response_chunks = [
                    "我理解您的问题",
                    "，让我为您详细分析",
                    "一下这个情况。",
                    "\n\n首先，",
                    "我们需要考虑",
                    "以下几个方面：",
                    "\n\n1. 技术可行性",
                    "\n2. 实现成本",
                    "\n3. 维护难度"
                ]
                
                for chunk in response_chunks:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.1)  # 模拟实际的流式延迟
                
            except Exception as llm_error:
                yield f"data: {json.dumps({'type': 'error', 'content': f'AI响应失败: {str(llm_error)}'})}\n\n"
                return
            
            processing_time = time.time() - start_time
            
            # 保存AI响应
            ai_message = Message(
                conversation_id=int(conversation_id),
                role="assistant",
                content=full_response,
                tokens=len(full_response.split()),  # 简化的token计算
                model_used=model.model,
                processing_time=processing_time,
                prompt_template_id=int(message_in.prompt_template_id) if message_in.prompt_template_id else None
            )
            db.add(ai_message)
            
            # 更新对话统计
            conversation.total_tokens += len(full_response.split())
            conversation.message_count += 2
            conversation.last_message_at = datetime.utcnow().isoformat()
            db.add(conversation)
            
            db.commit()
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'content': full_response, 'message_id': str(ai_message.id)})}\n\n"
            
        except Exception as e:
            db.rollback()
            yield f"data: {json.dumps({'type': 'error', 'content': f'发送消息失败: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.put("/conversations/{conversation_id}", tags=["AI对话"])
def update_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_id: str,
    conversation_in: ConversationUpdate,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """更新对话"""
    try:
        conversation = db.exec(
            select(Conversation).where(
                Conversation.id == int(conversation_id),
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="对话不存在"
            )
        
        if conversation_in.title:
            conversation.title = conversation_in.title
        
        db.add(conversation)
        db.commit()
        
        return StandardJSONResponse(
            content={
                "id": str(conversation.id),
                "title": conversation.title
            },
            message="对话更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新对话失败: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", tags=["AI对话"])
def delete_conversation(
    *,
    db: Session = Depends(get_db),
    conversation_id: str,
    user_id: int = 1  # TODO: 从认证中获取用户ID
):
    """删除对话"""
    try:
        conversation = db.exec(
            select(Conversation).where(
                Conversation.id == int(conversation_id),
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="对话不存在"
            )
        
        # 软删除
        conversation.is_active = False
        db.add(conversation)
        db.commit()
        
        return StandardJSONResponse(
            content=None,
            message="对话删除成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"删除对话失败: {str(e)}"
        )
