"""
Global error handler middleware
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle generic exceptions
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc) if __debug__ else "An unexpected error occurred",
            },
        },
    )


async def http_exception_handler(request: Request, exc):
    """
    Handle HTTP exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.detail.upper().replace(" ", "_"),
                "message": exc.detail,
            },
        },
    )


async def validation_exception_handler(request: Request, exc):
    """
    Handle validation errors
    """
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors,
            },
        },
    )


def add_exception_handlers(app: FastAPI):
    """
    Add all exception handlers to the app
    """
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
