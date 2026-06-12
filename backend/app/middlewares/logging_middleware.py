# app/middlewares/logging_middleware.py
"""
请求日志中间件
职责：
- 记录每个请求的方法、路径、状态码、耗时
- 便于调试智能体调用链
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app.request")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            "[%s] --> %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "[%s] <-- %s %s failed after %.2fms",
                request_id,
                request.method,
                request.url.path,
                duration,
            )
            raise

        duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            "[%s] <-- %s %s %s %.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        response.headers["X-Request-ID"] = request_id
        return response