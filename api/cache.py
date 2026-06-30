"""Redis cache helper with get/set/invalidate."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from .config import settings

_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool


async def disconnect_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _make_key(prefix: str, **params: Any) -> str:
    raw = json.dumps(params, sort_keys=True, default=str)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"mrp:{prefix}:{h}"


async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    val = await r.get(key)
    if val is not None:
        return json.loads(val)
    return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    r = await get_redis()
    await r.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_invalidate(prefix: str) -> None:
    r = await get_redis()
    async for key in r.scan_iter(match=f"mrp:{prefix}:*"):
        await r.delete(key)
