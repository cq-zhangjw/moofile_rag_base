"""Business exceptions and FastAPI exception handlers."""
from fastapi import Request
from fastapi.responses import JSONResponse

from . import responses


class BizError(Exception):
    def __init__(self, code: int, message: str, status_code: int = 200):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(BizError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(responses.ERR_NOT_FOUND, message, status_code=404)


class ConflictError(BizError):
    def __init__(self, message: str = "资源已存在"):
        super().__init__(responses.ERR_CONFLICT, message, status_code=409)


class BadRequestError(BizError):
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(responses.ERR_BAD_REQUEST, message, status_code=400)


async def biz_exception_handler(_: Request, exc: BizError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=responses.error(exc.code, exc.message),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=responses.error(responses.ERR_INTERNAL, f"服务器内部错误: {exc}"),
    )
