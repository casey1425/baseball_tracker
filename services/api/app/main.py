"""FastAPI entrypoint for the KBO Tracker backend."""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .naver import UpstreamError
from .routes import router


def create_app():
    application = FastAPI(
        title="KBO Live Tracker API",
        version="1.0.0",
        description="KBO schedules, live relay, highlights, summaries, and standings.",
    )
    origins = os.getenv(
        "KBO_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501",
    ).split(",")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in origins if origin.strip()],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix="/api/v1")

    @application.exception_handler(UpstreamError)
    async def upstream_error_handler(_request: Request, exc: UpstreamError):
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    return application


app = create_app()
