# app/middlewares/exception_handler.py
"""
全局异常处理
职责：
- 统一捕获core/exceptions.py中定义的业务异常
- 统一捕获FastAPI/Pydantic校验异常与未知异常
- 转换为统一响应格式返回前端
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger("app.exception")


def _error_response(code: str, message: str, status_code: int, extra: dict | None = None):
    body = {
        "code": code,
        "message": message,
        "data": None,
    }
    if extra:
        body["extra"] = extra
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器，供main.py在创建app时调用"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """业务异常：余票不足、预约冲突、鉴权失败等"""
        logger.warning(
            "AppException: code=%s message=%s path=%s",
            exc.code,
            exc.message,
            request.url.path,
        )
        return _error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            extra=getattr(exc, "extra", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求参数校验失败（FastAPI/Pydantic自动触发）"""
        logger.info("RequestValidationError: %s path=%s", exc.errors(), request.url.path)
        return _error_response(
            code="REQUEST_VALIDATION_ERROR",
            message="请求参数校验失败",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            extra={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """兜底：未预期的异常，避免500错误堆栈直接暴露给前端"""
        logger.exception("Unhandled exception path=%s", request.url.path)
        return _error_response(
            code="INTERNAL_SERVER_ERROR",
            message="服务器内部错误，请稍后重试",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )