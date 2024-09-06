from typing import Awaitable, Callable

import loguru
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.types import ASGIApp

from .paths import LOG_DIR

_CallNext = Callable[[Request], Awaitable[StreamingResponse]]

loguru.logger.add(
    LOG_DIR / "request_errors.log",
    filter=lambda record: record["extra"].get("name") == "request_errors",
    rotation="10 MB",
    retention=2,
)
_LOGGER = loguru.logger.bind(name="request_errors")


class ErrorLog(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None):
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: _CallNext):
        try:
            resp = await call_next(request)
            return resp
        except:
            _LOGGER.exception("Unhandled exception")
            raise


def log_http_exceptions(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def handler(request: Request, exc: HTTPException):
        request_str = await _pprint_request(request)
        _LOGGER.error(f"HTTPException {exc}\n{request_str}")
        return await http_exception_handler(request, exc)


def log_422s(app: FastAPI):
    from fastapi import Request, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):

        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        # or logger.error(f'{exc}')
        print(request, exc_str)
        content = {"status_code": 10422, "message": exc_str, "data": None}
        return JSONResponse(
            content=content,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


async def _pprint_request(request: Request):
    data = dict()

    try:
        data["body"] = await request.json()
    except Exception as err:
        data["body"] = await request.body()

    try:
        data["headers"] = dict(request.headers.items())
        data["query_params"] = dict(request.query_params.items())
    finally:
        return data
