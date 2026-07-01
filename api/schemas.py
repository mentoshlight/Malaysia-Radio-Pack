"""Pydantic v2 schemas — attribute names match ORM models (= actual DB columns)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=500)


class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int


class StateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    abbr: str
    region: Optional[str] = None
    capital: Optional[str] = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


class RepeaterBase(BaseModel):
    name: str
    callsign: Optional[str] = None
    rx_freq: float
    tx_freq: float
    offset: Optional[float] = None
    offset_dir: Optional[str] = None
    tone: Optional[float] = None
    tone_type: Optional[str] = None
    dcs_code: Optional[int] = None
    bandwidth: Optional[str] = None
    mode: Optional[str] = None
    duplex: Optional[str] = None
    power: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    coverage_radius: Optional[int] = None
    state_id: Optional[int] = None
    country: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
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
    dcs_code: Optional[int] = None
    bandwidth: Optional[str] = None
    mode: Optional[str] = None
    duplex: Optional[str] = None
    power: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    coverage_radius: Optional[int] = None
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
    state: Optional[str] = None  # populated via join with states table
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SimplexChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    band: Optional[str] = None
    mode: Optional[str] = None
    tone: Optional[float] = None
    tone_type: Optional[str] = None
    power: Optional[float] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class MarineChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_number: Optional[str] = None
    name: Optional[str] = None
    tx_freq: float
    rx_freq: Optional[float] = None
    mode: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class AviationFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    airport: Optional[str] = None
    service_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class AprsObjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    callsign: str
    name: Optional[str] = None
    frequency: Optional[float] = None
    type: Optional[str] = None
    symbol: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    status: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None


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
    category: Optional[str] = None
    notes: Optional[str] = None


class EmergencyFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    service: Optional[str] = None
    mode: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class CallingFreqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    frequency: float
    band: Optional[str] = None
    mode: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class TableCount(BaseModel):
    table: str
    count: int


class StateCount(BaseModel):
    state: str
    count: int


class ModeCount(BaseModel):
    mode: str
    count: int


class BandCount(BaseModel):
    band: str
    count: int


class StatsResponse(BaseModel):
    tables: List[TableCount]
    by_state: List[StateCount]
    by_mode: List[ModeCount]
    by_band: List[BandCount] = []
