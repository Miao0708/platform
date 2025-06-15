"""
详细的应用日志配置
"""
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import structlog


# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if False else structlog.dev.ConsoleRenderer(colors=True)
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 获取结构化日志器
logger = structlog.get_logger()


class DetailedLoggingMiddleware:
    """详细的请求/响应日志中间件"""
    
    def __init__(self, app: ASGIApp, enable_detailed_logging: bool = True):
        self.app = app
        self.enable_detailed_logging = enable_detailed_logging
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enable_detailed_logging:
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        # 缓存请求体
        body = b""
        
        async def receive_wrapper():
            nonlocal body
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
            return message
        
        # 记录请求信息
        await self._log_request(scope, body, request_id)
        
        # 处理响应
        response_started = False
        status_code = 500
        response_headers = {}
        
        async def send_wrapper(message):
            nonlocal response_started, status_code, response_headers
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                response_headers = dict(message.get("headers", []))
            elif message["type"] == "http.response.body" and not message.get("more_body", False):
                # 响应结束，记录日志
                process_time = time.time() - start_time
                await self._log_response(status_code, response_headers, request_id, process_time)
            await send(message)
        
        await self.app(scope, receive_wrapper, send_wrapper)
    
    async def _log_request(self, scope: dict, body: bytes, request_id: str):
        """记录请求详细信息"""
        if not self.enable_detailed_logging:
            return
        
        # 解析请求体
        body_data = None
        if body and scope["method"] in ["POST", "PUT", "PATCH"]:
            try:
                body_str = body.decode('utf-8')
                # 尝试解析JSON
                try:
                    body_data = json.loads(body_str)
                except json.JSONDecodeError:
                    body_data = body_str
            except Exception:
                body_data = "无法解析请求体"
        
        # 获取查询参数
        query_string = scope.get("query_string", b"").decode('utf-8')
        query_params = {}
        if query_string:
            from urllib.parse import parse_qs
            query_params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(query_string).items()}
        
        # 获取请求头（过滤敏感信息）
        headers = dict(scope.get("headers", []))
        # 转换字节到字符串
        headers = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v 
                  for k, v in headers.items()}
        
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        filtered_headers = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered_headers[key] = "***"
            else:
                filtered_headers[key] = value
        
        # 构建URL
        scheme = scope.get("scheme", "http")
        server = scope.get("server", ("localhost", 8000))
        path = scope.get("path", "/")
        full_url = f"{scheme}://{server[0]}:{server[1]}{path}"
        if query_string:
            full_url += f"?{query_string}"
        
        logger.info(
            "📥 HTTP请求详情",
            request_id=request_id,
            method=scope["method"],
            url=full_url,
            path=path,
            client_host=scope.get("client", ["unknown", 0])[0],
            user_agent=headers.get("user-agent", "unknown"),
            headers=filtered_headers,
            query_params=query_params,
            body=body_data,
            timestamp=datetime.now().isoformat()
        )
    
    async def _log_response(self, status_code: int, response_headers: dict, request_id: str, process_time: float):
        """记录响应详细信息"""
        if not self.enable_detailed_logging:
            return
        
        # 转换响应头字节到字符串
        headers = {}
        for key, value in response_headers.items():
            if isinstance(key, bytes):
                key = key.decode()
            if isinstance(value, bytes):
                value = value.decode()
            headers[key] = value
        
        logger.info(
            "📤 HTTP响应详情",
            request_id=request_id,
            status_code=status_code,
            headers=headers,
            process_time_ms=round(process_time * 1000, 2),
            timestamp=datetime.now().isoformat()
        )


class DatabaseLoggingMiddleware:
    """数据库操作日志中间件"""
    
    @staticmethod
    def log_sql_query(query: str, params: Optional[Dict[str, Any]] = None, execution_time: float = 0.0):
        """记录SQL查询"""
        logger.info(
            "🗄️ 数据库查询",
            query=query,
            params=params,
            execution_time_ms=round(execution_time * 1000, 2),
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def log_sql_error(query: str, error: str, params: Optional[Dict[str, Any]] = None):
        """记录SQL错误"""
        logger.error(
            "❌ 数据库错误",
            query=query,
            error=error,
            params=params,
            timestamp=datetime.now().isoformat()
        )


def log_api_call(endpoint: str, method: str, **kwargs):
    """记录API调用"""
    logger.info(
        "🔌 API调用",
        endpoint=endpoint,
        method=method,
        details=kwargs,
        timestamp=datetime.now().isoformat()
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """记录错误信息"""
    logger.error(
        "💥 系统错误",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        timestamp=datetime.now().isoformat(),
        exc_info=True
    )


def log_performance(operation: str, duration: float, **metadata):
    """记录性能指标"""
    logger.info(
        "⚡ 性能指标",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        metadata=metadata,
        timestamp=datetime.now().isoformat()
    )


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """设置日志配置"""
    # 设置根日志级别
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    logger.info("📋 日志系统初始化完成", log_level=log_level, log_file=log_file)


# 创建全局数据库日志器
db_logger = DatabaseLoggingMiddleware() 