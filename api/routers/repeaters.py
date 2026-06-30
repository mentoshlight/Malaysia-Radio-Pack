"""CRUD + nearby search for repeaters."""

from __future__ import annotations

import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import _make_key, cache_get, cache_invalidate, cache_set
from ..database import get_db
from ..models import Repeater
from ..schemas import PageParams, PageResponse, RepeaterCreate, RepeaterRead, RepeaterUpdate

router = APIRouter(prefix="/repeaters", tags=["Repeaters"])


# ── helpers ─────────────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── list ────────────────────────────────────────────────────────────────────

@router.get("/", response_model=PageResponse[RepeaterRead], summary="List repeaters")
async def list_repeaters(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    state_id: Optional[int] = None,
    mode: Optional[str] = None,
    band: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    cache_key = _make_key("repeaters_list", page=page, size=size, state_id=state_id, mode=mode, band=band, status=status, category=category, search=search)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    q = select(Repeater)
    count_q = select(func.count(Repeater.id))

    if state_id is not None:
        q = q.where(Repeater.state_id == state_id)
        count_q = count_q.where(Repeater.state_id == state_id)
    if mode:
        q = q.where(Repeater.mode == mode)
        count_q = count_q.where(Repeater.mode == mode)
    if status:
        q = q.where(Repeater.status == status)
        count_q = count_q.where(Repeater.status == status)
    if category:
        q = q.where(Repeater.category == category)
        count_q = count_q.where(Repeater.category == category)
    if search:
        pattern = f"%{search}%"
        q = q.where(Repeater.name.ilike(pattern) | Repeater.callsign.ilike(pattern))
        count_q = count_q.where(Repeater.name.ilike(pattern) | Repeater.callsign.ilike(pattern))

    total = (await db.execute(count_q)).scalar_one()
    pages = max(1, math.ceil(total / size))
    rows = (await db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()

    result = PageResponse(
        items=[RepeaterRead.model_validate(r) for r in rows],
        total=total,
        page=page,
        pages=pages,
    ).model_dump()
    await cache_set(cache_key, result)
    return result


# ── get by id ───────────────────────────────────────────────────────────────

@router.get("/{repeater_id}", response_model=RepeaterRead, summary="Get repeater by ID")
async def get_repeater(repeater_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    r = await db.get(Repeater, repeater_id)
    if not r:
        raise HTTPException(404, "Repeater not found")
    return r


# ── create ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=RepeaterRead, status_code=201, summary="Create repeater")
async def create_repeater(data: RepeaterCreate, db: AsyncSession = Depends(get_db)):
    r = Repeater(**data.model_dump())
    db.add(r)
    await db.flush()
    await db.refresh(r)
    await cache_invalidate("repeaters_list")
    return r


# ── update ──────────────────────────────────────────────────────────────────

@router.put("/{repeater_id}", response_model=RepeaterRead, summary="Update repeater")
async def update_repeater(repeater_id: uuid.UUID, data: RepeaterUpdate, db: AsyncSession = Depends(get_db)):
    r = await db.get(Repeater, repeater_id)
    if not r:
        raise HTTPException(404, "Repeater not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.flush()
    await db.refresh(r)
    await cache_invalidate("repeaters_list")
    return r


# ── delete ──────────────────────────────────────────────────────────────────

@router.delete("/{repeater_id}", status_code=204, summary="Delete repeater")
async def delete_repeater(repeater_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    r = await db.get(Repeater, repeater_id)
    if not r:
        raise HTTPException(404, "Repeater not found")
    await db.delete(r)
    await cache_invalidate("repeaters_list")


# ── nearby search ───────────────────────────────────────────────────────────

@router.get("/nearby/search", response_model=list[RepeaterRead], summary="Find nearby repeaters")
async def nearby_repeaters(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, ge=0.1, le=500, description="Search radius in km"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    # Try PostGIS ST_DWithin first
    try:
        sql = text("""
            SELECT * FROM repeaters
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND ST_DWithin(
                    ST_MakePoint(longitude, latitude)::geography,
                    ST_MakePoint(:lng, :lat)::geography,
                    :radius_m
                  )
            LIMIT :lim
        """)
        result = await db.execute(sql, {"lat": lat, "lng": lng, "radius_m": radius_km * 1000, "lim": limit})
        rows = result.mappings().all()
        if rows:
            return [RepeaterRead.model_validate(dict(r)) for r in rows]
    except Exception:
        pass  # PostGIS not available, fall through to Haversine

    # Haversine fallback
    q = select(Repeater).where(Repeater.latitude.is_not(None), Repeater.longitude.is_not(None))
    all_rows = (await db.execute(q)).scalars().all()
    nearby = []
    for r in all_rows:
        d = _haversine_km(lat, lng, r.latitude, r.longitude)
        if d <= radius_km:
            nearby.append((d, r))
    nearby.sort(key=lambda x: x[0])
    return [RepeaterRead.model_validate(r) for _, r in nearby[:limit]]
