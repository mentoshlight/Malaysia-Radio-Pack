"""Read-only endpoints for simplex, marine, aviation, aprs, satellites, emergency, calling frequencies."""

from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import _make_key, cache_get, cache_set
from ..database import get_db
from ..models import AprsObject, AviationFreq, CallingFreq, EmergencyFreq, MarineChannel, Satellite, SimplexChannel
from ..schemas import (
    AprsObjectRead,
    AviationFreqRead,
    CallingFreqRead,
    EmergencyFreqRead,
    MarineChannelRead,
    PageResponse,
    SatelliteRead,
    SimplexChannelRead,
)

router = APIRouter(prefix="/channels", tags=["Channels"])


async def _paginated(db: AsyncSession, model, schema, page: int, size: int, cache_prefix: str, **filters):
    cache_key = _make_key(cache_prefix, page=page, size=size, **filters)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    q = select(model)
    count_q = select(func.count(model.id))

    for field, value in filters.items():
        if value is not None:
            col = getattr(model, field)
            q = q.where(col == value)
            count_q = count_q.where(col == value)

    total = (await db.execute(count_q)).scalar_one()
    pages = max(1, math.ceil(total / size))
    rows = (await db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()

    result = PageResponse(
        items=[schema.model_validate(r) for r in rows],
        total=total, page=page, pages=pages,
    ).model_dump()
    await cache_set(cache_key, result)
    return result


# ── Simplex ─────────────────────────────────────────────────────────────────

@router.get("/simplex", response_model=PageResponse[SimplexChannelRead], summary="List simplex channels")
async def list_simplex(
    page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500),
    mode: Optional[str] = None, category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await _paginated(db, SimplexChannel, SimplexChannelRead, page, size, "simplex", mode=mode, category=category)


# ── Marine ──────────────────────────────────────────────────────────────────

@router.get("/marine", response_model=PageResponse[MarineChannelRead], summary="List marine channels")
async def list_marine(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await _paginated(db, MarineChannel, MarineChannelRead, page, size, "marine")


# ── Aviation ────────────────────────────────────────────────────────────────

@router.get("/aviation", response_model=PageResponse[AviationFreqRead], summary="List aviation frequencies")
async def list_aviation(
    page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500),
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await _paginated(db, AviationFreq, AviationFreqRead, page, size, "aviation", type=type)


# ── APRS ────────────────────────────────────────────────────────────────────

@router.get("/aprs", response_model=PageResponse[AprsObjectRead], summary="List APRS objects")
async def list_aprs(
    page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500),
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await _paginated(db, AprsObject, AprsObjectRead, page, size, "aprs", type=type)


# ── Satellites ──────────────────────────────────────────────────────────────

@router.get("/satellites", response_model=PageResponse[SatelliteRead], summary="List satellites")
async def list_satellites(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await _paginated(db, Satellite, SatelliteRead, page, size, "satellites")


# ── Emergency ───────────────────────────────────────────────────────────────

@router.get("/emergency", response_model=PageResponse[EmergencyFreqRead], summary="List emergency frequencies")
async def list_emergency(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await _paginated(db, EmergencyFreq, EmergencyFreqRead, page, size, "emergency")


# ── Calling ─────────────────────────────────────────────────────────────────

@router.get("/calling", response_model=PageResponse[CallingFreqRead], summary="List calling frequencies")
async def list_calling(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await _paginated(db, CallingFreq, CallingFreqRead, page, size, "calling")
