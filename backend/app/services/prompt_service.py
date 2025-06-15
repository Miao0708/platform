"""
Prompt模板服务
处理Prompt链式调用、变量替换等复杂逻辑
"""
import re
import time
from typing import Dict, Any, List, Tuple, Optional
from sqlmodel import Session
from app.crud.crud_prompt import prompt_template
from app.schemas.prompt import PromptValidateResponse


class PromptService:
    """Prompt服务类"""
    
    def __init__(self):
        # 匹配 {{GENERATE_FROM:identifier}} 的正则表达式
        self.chain_pattern = re.compile(r'\{\{GENERATE_FROM:(\w+)\}\}')
        # 匹配 {{variable}} 的正则表达式
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
    
    def validate_prompt(
        self, content: str, variables: Dict[str, Any] = None
    ) -> PromptValidateResponse:
        """
        验证Prompt内容
        
        Args:
            content: Prompt内容
            variables: 测试变量
            
        Returns:
            验证结果
        """
        if variables is None:
            variables = {}
        
        errors = []
        warnings = []
        variables_found = []
        chained_prompts = []
        
        # 查找所有变量
        variable_matches = self.variable_pattern.findall(content)
        for var in variable_matches:
            if var not in variables_found:
                variables_found.append(var)
        
        # 查找链式调用的Prompt
        chain_matches = self.chain_pattern.findall(content)
        for identifier in chain_matches:
            if identifier not in chained_prompts:
                chained_prompts.append(identifier)
        
        # 检查变量是否都有值
        for var in variables_found:
            if var not in variables and not var.startswith('GENERATE_FROM'):
                warnings.append(f"变量 '{var}' 没有提供值")
        
        # 尝试解析内容
        resolved_content = None
        try:
            # 简单的变量替换测试（不执行链式调用）
            test_content = content
            for var, value in variables.items():
                test_content = test_content.replace(f'{{{{{var}}}}}', str(value))
            
            # 将链式调用替换为占位符
            for identifier in chained_prompts:
                test_content = test_content.replace(
                    f'{{{{GENERATE_FROM:{identifier}}}}}',
                    f'[CHAINED_PROMPT:{identifier}]'
                )
            
            resolved_content = test_content
            
        except Exception as e:
            errors.append(f"解析失败: {str(e)}")
        
        is_valid = len(errors) == 0
        
        return PromptValidateResponse(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            resolved_content=resolved_content,
            variables_found=variables_found,
            chained_prompts=chained_prompts
        )
    
    async def resolve_prompt_content(
        self, db: Session, content: str, variables: Dict[str, Any],
        max_depth: int = 5, current_depth: int = 0
    ) -> str:
        """
        解析Prompt内容，处理链式调用
        
        Args:
            db: 数据库会话
            content: Prompt内容
            variables: 变量字典
            max_depth: 最大递归深度
            current_depth: 当前递归深度
            
        Returns:
            解析后的内容
        """
        if current_depth >= max_depth:
            raise ValueError(f"Prompt链式调用深度超过限制 ({max_depth})")
        
        # 查找并处理链式调用
        while True:
            match = self.chain_pattern.search(content)
            if not match:
                break
            
            identifier = match.group(1)
            
            # 查找子Prompt模板
            sub_template = prompt_template.get_by_identifier(db, identifier=identifier)
            if not sub_template:
                raise ValueError(f"Prompt模板 '{identifier}' 不存在")
            
            if not sub_template.is_active:
                raise ValueError(f"Prompt模板 '{identifier}' 未激活")
            
            # 递归解析子Prompt
            resolved_sub_content = await self.resolve_prompt_content(
                db, sub_template.content, variables, max_depth, current_depth + 1
            )
            
            # 这里应该调用LLM生成内容，暂时返回解析后的内容
            # TODO: 集成LLM客户端
            sub_prompt_output = f"[LLM_OUTPUT_FOR:{identifier}]\n{resolved_sub_content}"
            
            # 替换占位符
            content = content.replace(match.group(0), sub_prompt_output)
        
        # 替换常规变量
        for key, value in variables.items():
            content = content.replace(f'{{{{{key}}}}}', str(value))
        
        return content
    
    def extract_variables(self, content: str) -> List[str]:
        """提取Prompt中的所有变量"""
        variables = []
        
        # 提取普通变量
        variable_matches = self.variable_pattern.findall(content)
        for var in variable_matches:
            if var not in variables:
                variables.append(var)
        
        return variables
    
    def extract_chained_prompts(self, content: str) -> List[str]:
        """提取Prompt中的链式调用"""
        chained_prompts = []
        
        chain_matches = self.chain_pattern.findall(content)
        for identifier in chain_matches:
            if identifier not in chained_prompts:
                chained_prompts.append(identifier)
        
        return chained_prompts


# 创建服务实例
prompt_service = PromptService()
