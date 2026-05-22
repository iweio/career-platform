from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"success": False, "error": "Validation error", "details": exc.errors()},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 401:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Not authenticated"},
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )

    @app.exception_handler(Exception)
    async def global_handler(request: Request, exc: Exception):
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )
