"""
性能监控和日志记录工具
"""
import time
import logging
from functools import wraps
from typing import Callable, Any, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def performance_monitor(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > 5.0:  # 超过5秒记录警告
                    logger.warning(f"慢操作 {name}: {execution_time:.2f}s")
                else:
                    logger.info(f"操作完成 {name}: {execution_time:.2f}s")
                    
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"操作失败 {name}: {execution_time:.2f}s - {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > 2.0:  # 超过2秒记录警告
                    logger.warning(f"慢操作 {name}: {execution_time:.2f}s")
                else:
                    logger.debug(f"操作完成 {name}: {execution_time:.2f}s")
                    
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"操作失败 {name}: {execution_time:.2f}s - {str(e)}")
                raise
        
        # 检查是否为异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def operation_context(operation_name: str, **context_data):
    """操作上下文管理器，用于记录详细的操作信息"""
    start_time = time.time()
    logger.info(f"开始操作: {operation_name}", extra=context_data)
    
    try:
        yield
        execution_time = time.time() - start_time
        logger.info(f"操作成功: {operation_name} ({execution_time:.2f}s)", extra=context_data)
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"操作失败: {operation_name} ({execution_time:.2f}s) - {str(e)}", 
            extra=context_data
        )
        raise


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, duration: float):
        """记录API调用指标"""
        key = f"{method} {endpoint}"
        if key not in self.metrics:
            self.metrics[key] = {
                "total_calls": 0,
                "success_calls": 0,
                "error_calls": 0,
                "total_duration": 0,
                "avg_duration": 0
            }
        
        self.metrics[key]["total_calls"] += 1
        self.metrics[key]["total_duration"] += duration
        
        if 200 <= status_code < 400:
            self.metrics[key]["success_calls"] += 1
        else:
            self.metrics[key]["error_calls"] += 1
        
        # 更新平均时长
        self.metrics[key]["avg_duration"] = (
            self.metrics[key]["total_duration"] / self.metrics[key]["total_calls"]
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            "total_endpoints": len(self.metrics),
            "endpoints": self.metrics
        }


# 全局指标收集器实例
metrics_collector = MetricsCollector() 