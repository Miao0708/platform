#!/usr/bin/env python3
"""
初始化Prompt模板和AI模型配置数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import create_engine, Session, select
from app.core.config import settings
from app.models.prompt import PromptTemplate
from app.models.ai_model import AIModelConfig


def init_prompt_templates(db: Session):
    """初始化Prompt模板数据"""
    
    prompt_templates = [
        {
            "name": "需求分析专家",
            "identifier": "requirement_analyst",
            "content": """你是一个专业的需求分析师，请帮我分析以下需求：

{{requirement}}

请从以下角度进行分析：
1. 功能需求分析
2. 非功能需求识别
3. 业务流程梳理
4. 风险点评估
5. 实现建议""",
            "description": "专门用于需求分析的Prompt模板",
            "category": "requirement",
            "tags": ["需求分析", "功能设计", "业务流程"],
            "variables": ["requirement"],
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "代码评审专家",
            "identifier": "code_reviewer",
            "content": """你是一个资深的代码评审专家，请对以下代码进行详细评审：

{{code_diff}}

请从以下方面进行评审：
1. 代码规范和风格
2. 安全漏洞检测
3. 性能优化建议
4. 逻辑错误识别
5. 最佳实践建议""",
            "description": "专门用于代码评审的Prompt模板",
            "category": "code_review",
            "tags": ["代码评审", "质量检查", "安全审计"],
            "variables": ["code_diff"],
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "测试用例生成器",
            "identifier": "test_case_generator",
            "content": """你是一个测试专家，请为以下需求生成详细的测试用例：

需求描述：{{requirement}}

请生成以下类型的测试用例：
1. 功能测试用例
2. 边界值测试用例
3. 异常场景测试用例
4. 性能测试用例
5. 安全测试用例

每个测试用例应包含：
- 测试目标
- 前置条件
- 测试步骤
- 预期结果
- 优先级""",
            "description": "根据需求生成测试用例的Prompt模板",
            "category": "test_case",
            "tags": ["测试用例", "质量保证", "自动化测试"],
            "variables": ["requirement"],
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "技术方案设计师",
            "identifier": "technical_architect",
            "content": """你是一个资深的技术架构师，请为以下需求设计技术方案：

{{requirement}}

请提供：
1. 技术栈选择和理由
2. 系统架构设计
3. 数据库设计要点
4. API设计规范
5. 部署和运维方案
6. 风险评估和应对策略""",
            "description": "技术方案设计的Prompt模板",
            "category": "general",
            "tags": ["技术架构", "系统设计", "技术方案"],
            "variables": ["requirement"],
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "Bug分析专家",
            "identifier": "bug_analyzer",
            "content": """你是一个Bug分析专家，请分析以下Bug信息：

错误描述：{{bug_description}}
错误代码（如有）：{{code_diff}}

请提供：
1. Bug根因分析
2. 影响范围评估
3. 修复方案建议
4. 预防措施
5. 测试验证建议""",
            "description": "Bug分析和修复建议的Prompt模板",
            "category": "code_review",
            "tags": ["Bug分析", "问题排查", "修复建议"],
            "variables": ["bug_description", "code_diff"],
            "is_active": True,
            "usage_count": 0
        }
    ]
    
    for template_data in prompt_templates:
        # 检查是否已存在
        existing = db.exec(select(PromptTemplate).where(PromptTemplate.identifier == template_data["identifier"])).first()
        
        if not existing:
            template = PromptTemplate(**template_data)
            db.add(template)
            print(f"创建Prompt模板: {template_data['name']}")
        else:
            print(f"Prompt模板已存在: {template_data['name']}")
    
    db.commit()


def init_ai_models(db: Session):
    """初始化AI模型配置数据"""
    
    ai_models = [
        {
            "name": "OpenAI GPT-4o",
            "provider": "openai",
            "base_url": "https://api.openai.com/v1",
            "api_key": "your-openai-api-key-here",
            "model": "gpt-4o",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_default": True,
            "is_active": True,
            "timeout": 60,
            "usage_count": 0,
            "total_tokens_used": 0
        },
        {
            "name": "DeepSeek Chat",
            "provider": "deepseek",
            "base_url": "https://api.deepseek.com/v1",
            "api_key": "your-deepseek-api-key-here",
            "model": "deepseek-chat",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_default": False,
            "is_active": True,
            "timeout": 60,
            "usage_count": 0,
            "total_tokens_used": 0
        },
        {
            "name": "DeepSeek Coder",
            "provider": "deepseek",
            "base_url": "https://api.deepseek.com/v1",
            "api_key": "your-deepseek-api-key-here",
            "model": "deepseek-coder",
            "max_tokens": 4096,
            "temperature": 0.1,
            "is_default": False,
            "is_active": True,
            "timeout": 60,
            "usage_count": 0,
            "total_tokens_used": 0
        }
    ]
    
    for model_data in ai_models:
        # 检查是否已存在
        existing = db.query(AIModelConfig).filter(
            AIModelConfig.name == model_data["name"]
        ).first()
        
        if not existing:
            model = AIModelConfig(**model_data)
            db.add(model)
            print(f"创建AI模型配置: {model_data['name']}")
        else:
            print(f"AI模型配置已存在: {model_data['name']}")
    
    db.commit()


def main():
    """主函数"""
    print("开始初始化数据...")
    
    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    
    with Session(engine) as db:
        print("初始化Prompt模板...")
        init_prompt_templates(db)
        
        print("初始化AI模型配置...")
        init_ai_models(db)
    
    print("数据初始化完成！")


if __name__ == "__main__":
    main() 