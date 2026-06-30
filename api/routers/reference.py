"""Reference data: states, categories, stats."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import _make_key, cache_get, cache_set
from ..database import get_db
from ..models import (
    AprsObject,
    AviationFreq,
    CallingFreq,
    Category,
    EmergencyFreq,
    MarineChannel,
    Repeater,
    Satellite,
    SimplexChannel,
    State,
)
from ..schemas import CategoryRead, ModeCount, StateCount, StateRead, StatsResponse, TableCount

router = APIRouter(prefix="/reference", tags=["Reference"])

TABLES = [
    ("repeaters", Repeater),
    ("simplex_channels", SimplexChannel),
    ("marine_channels", MarineChannel),
    ("aviation_freqs", AviationFreq),
    ("aprs_objects", AprsObject),
    ("satellites", Satellite),
    ("emergency_freqs", EmergencyFreq),
    ("calling_freqs", CallingFreq),
]


@router.get("/states", response_model=list[StateRead], summary="List all states")
async def list_states(db: AsyncSession = Depends(get_db)):
    cached = await cache_get("mrp:states:all")
    if cached:
        return cached
    rows = (await db.execute(select(State).order_by(State.name))).scalars().all()
    result = [StateRead.model_validate(r).model_dump() for r in rows]
    await cache_set("mrp:states:all", result, ttl=3600)
    return result


@router.get("/categories", response_model=list[CategoryRead], summary="List all categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    cached = await cache_get("mrp:categories:all")
    if cached:
        return cached
    rows = (await db.execute(select(Category).order_by(Category.name))).scalars().all()
    result = [CategoryRead.model_validate(r).model_dump() for r in rows]
    await cache_set("mrp:categories:all", result, ttl=3600)
    return result


@router.get("/stats", response_model=StatsResponse, summary="Database statistics")
async def stats(db: AsyncSession = Depends(get_db)):
    cached = await cache_get("mrp:stats:all")
    if cached:
        return cached

    # per-table counts
    tables = []
    for name, model in TABLES:
        cnt = (await db.execute(select(func.count(model.id)))).scalar_one()
        tables.append(TableCount(table=name, count=cnt))

    # per-state counts (repeaters only)
    state_rows = (
        await db.execute(
            select(State.name, func.count(Repeater.id))
            .join(Repeater, Repeater.state_id == State.id, isouter=True)
            .group_by(State.name)
            .order_by(State.name)
        )
    ).all()
    by_state = [StateCount(state=name, count=cnt) for name, cnt in state_rows]

    # per-mode counts (repeaters only)
    mode_rows = (
        await db.execute(
            select(Repeater.mode, func.count(Repeater.id))
            .group_by(Repeater.mode)
            .order_by(Repeater.mode)
        )
    ).all()
    by_mode = [ModeCount(mode=m, count=cnt) for m, cnt in mode_rows]

    result = StatsResponse(tables=tables, by_state=by_state, by_mode=by_mode).model_dump()
    await cache_set("mrp:stats:all", result, ttl=120)
    return result
