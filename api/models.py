"""SQLAlchemy ORM models — attribute names MUST match actual DB column names exactly."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    abbr: Mapped[str] = mapped_column("abbreviation", String(10), nullable=False, unique=True)
    region: Mapped[Optional[str]] = mapped_column(String(50))
    capital: Mapped[Optional[str]] = mapped_column(String(100))
    repeaters: Mapped[list["Repeater"]] = relationship(back_populates="state_rel")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class Repeater(Base):
    __tablename__ = "repeaters"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    callsign: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    rx_freq: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    tx_freq: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    offset: Mapped[Optional[float]] = mapped_column(Numeric(8, 5))
    offset_dir: Mapped[Optional[str]] = mapped_column(String(10))
    tone: Mapped[Optional[float]] = mapped_column(Numeric(5, 1))
    tone_type: Mapped[Optional[str]] = mapped_column(String(10))
    dcs_code: Mapped[Optional[int]] = mapped_column(Integer)
    bandwidth: Mapped[Optional[str]] = mapped_column(String(10))
    mode: Mapped[Optional[str]] = mapped_column(String(10))
    duplex: Mapped[Optional[str]] = mapped_column(String(10))
    power: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    altitude: Mapped[Optional[int]] = mapped_column(Integer)
    coverage_radius: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("states.id"))
    country: Mapped[Optional[str]] = mapped_column(String(3))
    category: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(20))
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    state_rel: Mapped[Optional["State"]] = relationship(back_populates="repeaters")


class SimplexChannel(Base):
    __tablename__ = "simplex_channels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False, unique=True)
    band: Mapped[Optional[str]] = mapped_column(String(10))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    tone: Mapped[Optional[float]] = mapped_column(Numeric(5, 1))
    tone_type: Mapped[Optional[str]] = mapped_column(String(10))
    power: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class MarineChannel(Base):
    __tablename__ = "marine_channels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_number: Mapped[Optional[str]] = mapped_column(String(10))
    name: Mapped[Optional[str]] = mapped_column(String(100))
    tx_freq: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    rx_freq: Mapped[Optional[float]] = mapped_column(Numeric(10, 5))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class AviationFreq(Base):
    __tablename__ = "aviation_freqs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    frequency: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    airport: Mapped[Optional[str]] = mapped_column(String(100))
    service_type: Mapped[Optional[str]] = mapped_column(String(50))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class AprsObject(Base):
    __tablename__ = "aprs_objects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    callsign: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    frequency: Mapped[Optional[float]] = mapped_column(Numeric(10, 5))
    type: Mapped[Optional[str]] = mapped_column(String(30))
    symbol: Mapped[Optional[str]] = mapped_column(String(10))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    altitude: Mapped[Optional[int]] = mapped_column(Integer)
    state_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("states.id"))
    status: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class Satellite(Base):
    __tablename__ = "satellites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    norad_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    uplink: Mapped[Optional[float]] = mapped_column(Numeric(10, 5))
    downlink: Mapped[Optional[float]] = mapped_column(Numeric(10, 5))
    beacon: Mapped[Optional[float]] = mapped_column(Numeric(10, 5))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class EmergencyFreq(Base):
    __tablename__ = "emergency_freqs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    frequency: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    service: Mapped[Optional[str]] = mapped_column(String(50))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())


class CallingFreq(Base):
    __tablename__ = "calling_freqs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    frequency: Mapped[float] = mapped_column(Numeric(10, 5), nullable=False)
    band: Mapped[Optional[str]] = mapped_column(String(10))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
