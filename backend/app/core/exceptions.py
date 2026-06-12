"""
自定义异常
职责：
- 定义业务异常基类与各类业务异常（余票不足、预约冲突、鉴权失败等）
- 供middlewares/exception_handler.py统一捕获并转换为标准响应格式
"""


class AppException(Exception):
    """
    业务异常基类。
    所有service层抛出的业务异常都应继承该类，
    便于exception_handler统一捕获处理。
    """

    code: str = "APP_ERROR"
    status_code: int = 400
    message: str = "业务处理出现错误"

    def __init__(self, message: str | None = None, **extra):
        self.message = message or self.message
        self.extra = extra
        super().__init__(self.message)


# ---------- 通用 ----------
class NotFoundError(AppException):
    """资源不存在"""

    code = "NOT_FOUND"
    status_code = 404
    message = "请求的资源不存在"


class ValidationError(AppException):
    """业务参数校验失败（与pydantic的校验区分，用于service层业务规则校验）"""

    code = "VALIDATION_ERROR"
    status_code = 422
    message = "参数校验失败"


# ---------- 鉴权相关 ----------
class AuthenticationError(AppException):
    """鉴权失败（未登录/token无效）"""

    code = "AUTHENTICATION_ERROR"
    status_code = 401
    message = "鉴权失败，请重新登录"


class PermissionDeniedError(AppException):
    """权限不足"""

    code = "PERMISSION_DENIED"
    status_code = 403
    message = "权限不足，无法执行该操作"


# ---------- 用户相关 ----------
class UserNotFoundError(NotFoundError):
    code = "USER_NOT_FOUND"
    message = "用户不存在"


# ---------- 航班相关 ----------
class FlightNotFoundError(NotFoundError):
    code = "FLIGHT_NOT_FOUND"
    message = "航班不存在"


class InsufficientSeatsError(AppException):
    """余票不足"""

    code = "INSUFFICIENT_SEATS"
    status_code = 409
    message = "该航班余票不足"


# ---------- 预约/订单相关 ----------
class BookingNotFoundError(NotFoundError):
    code = "BOOKING_NOT_FOUND"
    message = "订单不存在"


class BookingConflictError(AppException):
    """预约冲突（如重复预约、状态机非法转换等）"""

    code = "BOOKING_CONFLICT"
    status_code = 409
    message = "预约存在冲突，无法完成操作"


class InvalidBookingStateError(AppException):
    """订单状态机非法转换"""

    code = "INVALID_BOOKING_STATE"
    status_code = 409
    message = "订单当前状态不支持该操作"


# ---------- Agent相关 ----------
class AgentExecutionError(AppException):
    """Agent执行过程中出现错误（如LLM调用失败、工具调用异常等）"""

    code = "AGENT_EXECUTION_ERROR"
    status_code = 500
    message = "智能体处理请求时出现错误"


class IntentRecognitionError(AppException):
    """意图识别失败"""

    code = "INTENT_RECOGNITION_ERROR"
    status_code = 500
    message = "意图识别失败"