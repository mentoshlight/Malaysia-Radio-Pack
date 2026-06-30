"""Pydantic v2 schemas for all MRP models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ── Pagination ──────────────────────────────────────────────────────────────

class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(50, ge=1, le=500, description="Items per page")


class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int


# ── State ───────────────────────────────────────────────────────────────────

class StateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    abbr: str
    region: Optional[str] = None
    capital: Optional[str] = None


# ── Category ────────────────────────────────────────────────────────────────

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


# ── Repeater ────────────────────────────────────────────────────────────────

class RepeaterBase(BaseModel):
    name: str
    callsign: Optional[str] = None
    rx_freq: float
    tx_freq: float
    offset: Optional[float] = None
    offset_dir: Optional[str] = None
    tone: Optional[float] = None
    tone_type: str = "none"
    dcs_code: Optional[str] = None
    bandwidth: str = "narrow"
    mode: str = "fm"
    duplex: str = "simplex"
    power: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    coverage_radius: Optional[float] = None
    state_id: Optional[int] = None
    country: str = "Malaysia"
    category: Optional[str] = None
    status: str = "active"
    last_verified: Optional[datetime] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class RepeaterCreate(RepeaterBase):
    pass


class RepeaterUpdate(BaseModel):
    name: Optional[str] = None
    callsign: Optional[str] = None
    rx_freq: Optional[float] = None
    tx_freq: Optional[float] = None
    offset: Optional[float] = None
    offset_dir: Optional[str] = None
    tone: Optional[float] = None
    tone_type: Optional[str] = None
    dcs_code: Optional[str] = None
    bandwidth: Optional[str] = None
    mode: Optional[str] = None
    duplex: Optional[str] = None
    power: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    coverage_radius: Optional[float] = None
    state_id: Optional[int] = None
    country: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    last_verified: Optional[datetime] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class RepeaterRead(RepeaterBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── SimplexChannel ──────────────────────────────────────────────────────────

class SimplexChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    rx_freq: float
    tx_freq: float
    tone: Optional[float] = None
    tone_type: str = "none"
    bandwidth: str = "narrow"
    mode: str = "fm"
    power: Optional[float] = None
    category: Optional[str] = None
    notes: Optional[str] = None


# ── MarineChannel ───────────────────────────────────────────────────────────

class MarineChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_num: Optional[str] = None
    name: str
    rx_freq: float
    tx_freq: float
    mode: str = "fm"
    power: Optional[float] = None
    notes: Optional[str] = None


# ── AviationFreq ────────────────────────────────────────────────────────────

class AviationFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    freq: float
    type: str
    airport: Optional[str] = None
    notes: Optional[str] = None


# ── AprsObject ──────────────────────────────────────────────────────────────

class AprsObjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    callsign: str
    frequency: Optional[float] = None
    symbol: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    type: str
    notes: Optional[str] = None


# ── Satellite ───────────────────────────────────────────────────────────────

class SatelliteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    norad_id: Optional[int] = None
    uplink: Optional[float] = None
    downlink: Optional[float] = None
    beacon: Optional[float] = None
    mode: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


# ── EmergencyFreq ───────────────────────────────────────────────────────────

class EmergencyFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    agency: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None


# ── CallingFreq ─────────────────────────────────────────────────────────────

class CallingFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    band: Optional[str] = None
    mode: Optional[str] = None
    notes: Optional[str] = None


# ── Stats ───────────────────────────────────────────────────────────────────

class TableCount(BaseModel):
    table: str
    count: int


class StateCount(BaseModel):
    state: str
    count: int


class ModeCount(BaseModel):
    mode: str
    count: int


class StatsResponse(BaseModel):
    tables: List[TableCount]
    by_state: List[StateCount]
    by_mode: List[ModeCount]
