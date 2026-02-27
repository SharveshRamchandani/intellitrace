"""
utils/exceptions.py
────────────────────
Custom exception classes and FastAPI exception handlers.
"""
from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class IntelliTraceException(Exception):
    """Base exception for all application errors."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(IntelliTraceException):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", status_code=404)


class ValidationError(IntelliTraceException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=422)


class FraudEngineError(IntelliTraceException):
    def __init__(self, detail: str):
        super().__init__(f"Fraud engine error: {detail}", status_code=500)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(IntelliTraceException)
    async def intellitrace_exception_handler(
        request: Request, exc: IntelliTraceException
    ) -> JSONResponse:
        logger.warning(
            "application_error",
            path=str(request.url),
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            path=str(request.url),
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
