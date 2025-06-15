"""
自定义异常类
提供更详细的错误信息和处理
"""
from typing import Any, Dict, Optional


class GitConfigError(Exception):
    """Git配置相关错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ModelFetchError(Exception):
    """模型拉取相关错误"""
    def __init__(self, provider: str, message: str, status_code: Optional[int] = None):
        self.provider = provider
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class PromptValidationError(Exception):
    """Prompt验证错误"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"字段 {field}: {message}")


class DatabaseIntegrityError(Exception):
    """数据库完整性错误"""
    def __init__(self, message: str, constraint: Optional[str] = None):
        self.message = message
        self.constraint = constraint
        super().__init__(self.message)


class ConfigurationError(Exception):
    """配置错误"""
    def __init__(self, component: str, message: str):
        self.component = component
        self.message = message
        super().__init__(f"配置错误 [{component}]: {message}") 