"""
LLM客户端封装，支持多种LLM API
"""
import json
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import httpx
from app.core.config import settings


class LLMResponse:
    """LLM响应封装"""
    
    def __init__(
        self, 
        content: str, 
        model: str, 
        tokens_used: int = 0,
        processing_time: float = 0.0,
        success: bool = True,
        error_message: str = None
    ):
        self.content = content
        self.model = model
        self.tokens_used = tokens_used
        self.processing_time = processing_time
        self.success = success
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "success": self.success,
            "error_message": self.error_message
        }


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """聊天完成接口"""
        pass
    
    @abstractmethod
    async def text_completion(
        self, 
        prompt: str, 
        **kwargs
    ) -> LLMResponse:
        """文本完成接口"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, base_url, model)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """OpenAI聊天完成"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                processing_time = time.time() - start_time
                
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    processing_time=processing_time,
                    success=True
                )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def text_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """OpenAI文本完成（通过聊天接口实现）"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, temperature, max_tokens, **kwargs)


class LocalLLMClient(BaseLLMClient):
    """本地LLM客户端（如Ollama）"""
    
    def __init__(self, api_key: str = "", base_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__(api_key, base_url, model)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """本地LLM聊天完成"""
        start_time = time.time()
        
        # 将消息转换为单个prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                processing_time = time.time() - start_time
                
                content = result.get("response", "")
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    tokens_used=0,  # 本地模型通常不返回token数
                    processing_time=processing_time,
                    success=True
                )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def text_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """本地LLM文本完成"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, temperature, **kwargs)


class LLMClientManager:
    """LLM客户端管理器"""
    
    def __init__(self):
        self._clients = {}
        self._default_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        # OpenAI客户端
        if settings.LLM_API_KEY:
            openai_client = OpenAIClient(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                model=settings.LLM_MODEL
            )
            self._clients["openai"] = openai_client
            if not self._default_client:
                self._default_client = openai_client
        
        # 本地LLM客户端
        local_client = LocalLLMClient()
        self._clients["local"] = local_client
        if not self._default_client:
            self._default_client = local_client
    
    def get_client(self, client_type: str = None) -> BaseLLMClient:
        """获取LLM客户端"""
        if client_type and client_type in self._clients:
            return self._clients[client_type]
        return self._default_client
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        client_type: str = None,
        **kwargs
    ) -> LLMResponse:
        """聊天完成"""
        client = self.get_client(client_type)
        if not client:
            return LLMResponse(
                content="",
                model="unknown",
                success=False,
                error_message="没有可用的LLM客户端"
            )
        
        return await client.chat_completion(messages, **kwargs)
    
    async def text_completion(
        self, 
        prompt: str, 
        client_type: str = None,
        **kwargs
    ) -> LLMResponse:
        """文本完成"""
        client = self.get_client(client_type)
        if not client:
            return LLMResponse(
                content="",
                model="unknown",
                success=False,
                error_message="没有可用的LLM客户端"
            )
        
        return await client.text_completion(prompt, **kwargs)
    
    async def parse_requirements(
        self, 
        content: str, 
        file_type: str = "text",
        **kwargs
    ) -> LLMResponse:
        """解析需求文档"""
        prompt = f"""
请分析以下{file_type}格式的需求文档，并提取结构化信息：

需求内容：
{content}

请按照以下JSON格式返回分析结果：
{{
    "summary": "需求摘要",
    "functional_requirements": ["功能需求1", "功能需求2"],
    "non_functional_requirements": ["非功能需求1", "非功能需求2"],
    "acceptance_criteria": ["验收标准1", "验收标准2"],
    "category": "需求分类",
    "priority": "优先级(low/medium/high/urgent)",
    "complexity": "复杂度(simple/medium/complex)",
    "estimated_hours": 预估工时数字,
    "dependencies": ["依赖项1", "依赖项2"],
    "risks": ["风险1", "风险2"]
}}

请确保返回有效的JSON格式。
"""
        
        return await self.text_completion(prompt, **kwargs)
    
    async def review_code(
        self, 
        code_diff: str, 
        requirements: str = "",
        focus_areas: List[str] = None,
        **kwargs
    ) -> LLMResponse:
        """代码评审"""
        focus_text = ""
        if focus_areas:
            focus_text = f"请特别关注以下方面：{', '.join(focus_areas)}"
        
        requirements_text = ""
        if requirements:
            requirements_text = f"\n相关需求：\n{requirements}\n"
        
        prompt = f"""
请对以下代码变更进行详细评审：

{requirements_text}
代码差异：
{code_diff}

{focus_text}

请按照以下JSON格式返回评审结果：
{{
    "summary": "评审摘要",
    "issues": [
        {{
            "type": "问题类型(security/performance/logic/style)",
            "severity": "严重程度(low/medium/high/critical)",
            "file": "文件名",
            "line": 行号,
            "description": "问题描述",
            "suggestion": "修改建议"
        }}
    ],
    "suggestions": ["改进建议1", "改进建议2"],
    "security_score": 安全评分(0-100),
    "quality_score": 质量评分(0-100),
    "complexity_analysis": {{
        "cyclomatic_complexity": 圈复杂度,
        "maintainability_index": 可维护性指数
    }},
    "positive_aspects": ["优点1", "优点2"]
}}

请确保返回有效的JSON格式。
"""
        
        return await self.text_completion(prompt, **kwargs)


# 创建全局LLM客户端管理器实例
llm_manager = LLMClientManager()
