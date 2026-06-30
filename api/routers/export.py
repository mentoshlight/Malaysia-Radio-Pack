"""Export endpoints: CHIRP, UV-5RM, UV-K5, AnyTone, JSON, CSV, YAML."""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

import yaml
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import _make_key, cache_get, cache_set
from ..database import get_db
from ..models import Repeater

router = APIRouter(prefix="/export", tags=["Export"])


async def _get_repeaters(
    db: AsyncSession,
    state_id: Optional[int],
    mode: Optional[str],
    band: Optional[str],
    category: Optional[str],
) -> list[dict]:
    q = select(Repeater)
    if state_id is not None:
        q = q.where(Repeater.state_id == state_id)
    if mode:
        q = q.where(Repeater.mode == mode)
    if category:
        q = q.where(Repeater.category == category)
    rows = (await db.execute(q)).scalars().all()
    return [
        {
            "name": r.name,
            "callsign": r.callsign,
            "rx_freq": float(r.rx_freq) if r.rx_freq else 0,
            "tx_freq": float(r.tx_freq) if r.tx_freq else 0,
            "offset": float(r.offset) if r.offset else 0,
            "offset_dir": r.offset_dir or "simplex",
            "tone": float(r.tone) if r.tone else 0,
            "tone_type": r.tone_type or "none",
            "dcs_code": r.dcs_code or "",
            "bandwidth": r.bandwidth or "narrow",
            "mode": r.mode or "fm",
            "duplex": r.duplex or "simplex",
            "power": r.power or 25,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "state_id": r.state_id,
            "category": r.category,
            "status": r.status,
            "notes": r.notes or "",
        }
        for r in rows
    ]


def _duplex_str(r: dict) -> str:
    d = r["duplex"]
    if d == "minus":
        return "-"
    if d == "plus":
        return "+"
    return ""


def _tone_str(r: dict) -> str:
    if r["tone_type"] == "ctcss":
        return "Tone"
    if r["tone_type"] == "dcs":
        return "DCS"
    return "Off"


# ── CHIRP CSV ───────────────────────────────────────────────────────────────

def _chirp_csv(repeaters: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "Location", "Name", "Frequency", "Duplex", "Offset", "Tone",
        "rToneFreq", "cToneFreq", "DtcsCode", "DtcsPolarity", "RxDtcsCode",
        "CrossMode", "Mode", "TStep", "Skip", "Power", "Comment",
    ])
    for i, r in enumerate(repeaters, 1):
        offset_mhz = abs(r["tx_freq"] - r["rx_freq"]) if r["tx_freq"] != r["rx_freq"] else 0.0
        chirp_mode = "FM" if r["mode"] == "fm" else r["mode"].upper()
        w.writerow([
            i,
            r["name"][:16],
            f"{r['rx_freq']:.5f}",
            _duplex_str(r),
            f"{offset_mhz:.5f}",
            _tone_str(r),
            f"{r['tone']:.1f}" if r["tone"] and r["tone_type"] == "ctcss" else "88.5",
            f"{r['tone']:.1f}" if r["tone"] and r["tone_type"] == "ctcss" else "88.5",
            r["dcs_code"] if r["tone_type"] == "dcs" else "023",
            "NN",
            "023",
            "Tone->Tone",
            chirp_mode,
            "5.00",
            "",
            f"{r['power']:.0f}" if r["power"] else "25",
            r["notes"][:50] if r["notes"] else "",
        ])
    return buf.getvalue()


# ── Baofeng UV-5RM CPS CSV ─────────────────────────────────────────────────

def _uv5rm_csv(repeaters: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["No.", "Channel Name", "Frequency", "Duplex", "Offset", "Tone Mode", "CTCSS/DCS", "Power", "Bandwidth", "Comment"])
    for i, r in enumerate(repeaters, 1):
        w.writerow([
            i, r["name"][:16], f"{r['rx_freq']:.5f}", _duplex_str(r).upper() or "OFF",
            f"{abs(r['tx_freq'] - r['rx_freq']):.5f}", _tone_str(r),
            f"{r['tone']:.1f}" if r["tone"] else "OFF",
            "HIGH" if (r["power"] or 0) >= 5 else "LOW",
            "NARR" if r["bandwidth"] == "narrow" else "WIDE",
            r["notes"][:30],
        ])
    return buf.getvalue()


# ── Quansheng UV-K5 CSV ────────────────────────────────────────────────────

def _uvk5_csv(repeaters: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Channel", "Name", "RX Freq", "TX Freq", "Power", "Bandwidth", "Tone", "DCS", "Mode"])
    for i, r in enumerate(repeaters, 1):
        w.writerow([
            i, r["name"][:16], f"{r['rx_freq']:.5f}", f"{r['tx_freq']:.5f}",
            "HIGH" if (r["power"] or 0) >= 5 else "LOW",
            "NARROW" if r["bandwidth"] == "narrow" else "WIDE",
            f"{r['tone']:.1f}" if r["tone"] and r["tone_type"] == "ctcss" else "",
            r["dcs_code"] if r["tone_type"] == "dcs" else "",
            r["mode"].upper(),
        ])
    return buf.getvalue()


# ── AnyTone CPS CSV ────────────────────────────────────────────────────────

def _anytone_csv(repeaters: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Channel Number", "Channel Name", "Receive Frequency", "Transmit Frequency",
                 "Channel Type", "Power", "Bandwidth", "CTCSS/DCS Encode", "CTCSS/DCS Decode", "Contact", "Group List"])
    for i, r in enumerate(repeaters, 1):
        w.writerow([
            i, r["name"][:16], f"{r['rx_freq']:.5f}", f"{r['tx_freq']:.5f}",
            "A-Analog" if r["mode"] == "fm" else "D-Digital",
            "High" if (r["power"] or 0) >= 5 else "Low",
            "12.5K" if r["bandwidth"] == "narrow" else "25K",
            f"{r['tone']:.1f}" if r["tone"] and r["tone_type"] == "ctcss" else "Off",
            f"{r['tone']:.1f}" if r["tone"] and r["tone_type"] == "ctcss" else "Off",
            "", "",
        ])
    return buf.getvalue()


# ── Endpoints ───────────────────────────────────────────────────────────────

async def _cached_export(db, state_id, mode, band, category, prefix, build_fn, content_type, ext):
    cache_key = _make_key(f"export_{prefix}", state_id=state_id, mode=mode, band=band, category=category)
    cached = await cache_get(cache_key)
    if cached:
        data = cached if isinstance(cached, str) else cached.get("data", "")
    else:
        repeaters = await _get_repeaters(db, state_id, mode, band, category)
        data = build_fn(repeaters)
        await cache_set(cache_key, {"data": data}, ttl=300)
    return StreamingResponse(io.BytesIO(data.encode()), media_type=content_type,
                             headers={"Content-Disposition": f"attachment; filename=mrp_export.{ext}"})


@router.get("/chirp", summary="Export CHIRP-compatible CSV")
async def export_chirp(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await _cached_export(db, state_id, mode, band, category, "chirp", _chirp_csv, "text/csv", "csv")


@router.get("/uv5rm", summary="Export Baofeng UV-5RM CPS CSV")
async def export_uv5rm(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await _cached_export(db, state_id, mode, band, category, "uv5rm", _uv5rm_csv, "text/csv", "csv")


@router.get("/uvk5", summary="Export Quansheng UV-K5 CSV")
async def export_uvk5(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await _cached_export(db, state_id, mode, band, category, "uvk5", _uvk5_csv, "text/csv", "csv")


@router.get("/anytone", summary="Export AnyTone CPS CSV")
async def export_anytone(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await _cached_export(db, state_id, mode, band, category, "anytone", _anytone_csv, "text/csv", "csv")


@router.get("/json", summary="Export full JSON dump")
async def export_json(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    cache_key = _make_key("export_json", state_id=state_id, mode=mode, band=band, category=category)
    cached = await cache_get(cache_key)
    if cached:
        data = cached if isinstance(cached, str) else json.dumps(cached)
    else:
        repeaters = await _get_repeaters(db, state_id, mode, band, category)
        data = json.dumps(repeaters, indent=2, default=str)
        await cache_set(cache_key, data, ttl=300)
    return StreamingResponse(io.BytesIO(data.encode()), media_type="application/json",
                             headers={"Content-Disposition": "attachment; filename=mrp_export.json"})


@router.get("/csv", summary="Export generic CSV")
async def export_csv(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    def _generic_csv(repeaters):
        if not repeaters:
            return ""
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=repeaters[0].keys())
        w.writeheader()
        w.writerows(repeaters)
        return buf.getvalue()

    return await _cached_export(db, state_id, mode, band, category, "csv", _generic_csv, "text/csv", "csv")


@router.get("/yaml", summary="Export YAML dump")
async def export_yaml(state_id: Optional[int] = None, mode: Optional[str] = None, band: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    cache_key = _make_key("export_yaml", state_id=state_id, mode=mode, band=band, category=category)
    cached = await cache_get(cache_key)
    if cached:
        data = cached if isinstance(cached, str) else yaml.dump(cached, default_flow_style=False)
    else:
        repeaters = await _get_repeaters(db, state_id, mode, band, category)
        data = yaml.dump(repeaters, default_flow_style=False)
        await cache_set(cache_key, data, ttl=300)
    return StreamingResponse(io.BytesIO(data.encode()), media_type="text/yaml",
                             headers={"Content-Disposition": "attachment; filename=mrp_export.yaml"})
