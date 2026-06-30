"""FastAPI application entry point for Malaysia Radio Pack v2.0."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .cache import disconnect_redis, get_redis
from .config import settings
from .routers import channels, export, reference, repeaters


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup – verify Redis connection
    try:
        r = await get_redis()
        await r.ping()
    except Exception:
        pass  # Redis is optional; degrade gracefully
    yield
    # shutdown
    await disconnect_redis()


app = FastAPI(
    title="Malaysia Radio Pack API",
    description="Comprehensive amateur radio repeater and frequency database for Malaysia.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,
)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repeaters.router, prefix=settings.API_PREFIX)
app.include_router(channels.router, prefix=settings.API_PREFIX)
app.include_router(reference.router, prefix=settings.API_PREFIX)
app.include_router(export.router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "2.0.0"}
