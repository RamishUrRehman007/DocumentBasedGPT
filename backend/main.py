import inspect
import logging
import os
import re
from typing import Callable

import config
import dto
import uvicorn  # type: ignore
from error_handler import exception_handler
from exceptions import DocumentBasedGPTError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse, Response
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from libs import log_sanitizer
from pydantic import BaseModel
from views import chat_view, file_view


def init_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s",
        level=config.LOG_LEVEL,
    )
    log_sanitizer.sanitize_formatters(logging.root.handlers)


def include_routers(app: FastAPI) -> None:
    app.include_router(file_view.router, prefix="/service/api/v1")
    app.include_router(chat_view.router, prefix="/service/api/v1")


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DocumentBasedGPTError, exception_handler)


def add_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def replace_content_type_header(
        request: Request, call_next: Callable
    ) -> Response:
        response = await call_next(request)
        if response.headers.get("content-type") == "application/json":
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response


def custom_openapi() -> dto.JSON:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DocumentBasedGPT Dev API",
        version=config.VERSION,
        routes=app.routes,
        servers=[{"url": "", "description": "default"}],
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        for method in getattr(route, "methods"):
            if re.search("get_current_user", inspect.getsource(endpoint)) or re.search(
                "jwt_refresh_token_required", inspect.getsource(endpoint)
            ):
                openapi_schema["paths"][path][method.lower()]["security"] = [
                    {"HTTPBearer": []}
                ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


init_logging()
app = FastAPI(
    title="DocumentBasedGPT",
    docs_url=config.ROOT_PATH + "/docs",
    openapi_url=(
        config.ROOT_PATH + "/openapi.json" if config.ENVIRONMENT == "dev" else None
    ),
)
app.openapi = custom_openapi  # type: ignore
include_routers(app)
add_exception_handlers(app)
add_middlewares(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
)


@app.get(config.ROOT_PATH)
async def root_view() -> RedirectResponse:
    return RedirectResponse(url=config.ROOT_PATH + "/docs", status_code=303)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10000,
        timeout_keep_alive=config.TIMEOUT,
        log_level=config.UVICORN_LOG_LEVEL,
        reload=config.ENABLE_RELOAD_UVICORN,
        workers=4,
    )
