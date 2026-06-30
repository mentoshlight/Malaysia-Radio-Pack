"""SQLAlchemy ORM models for all MRP tables."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    abbr: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    region: Mapped[Optional[str]] = mapped_column(String(50))
    capital: Mapped[Optional[str]] = mapped_column(String(100))

    repeaters: Mapped[list["Repeater"]] = relationship(back_populates="state_rel")

    def __repr__(self) -> str:
        return f"<State {self.abbr}: {self.name}>"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Repeater(Base):
    __tablename__ = "repeaters"
    __table_args__ = (
        Index("ix_repeaters_lat_lng", "latitude", "longitude"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    callsign: Mapped[Optional[str]] = mapped_column(String(20))
    rx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    tx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    offset: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))
    offset_dir: Mapped[Optional[str]] = mapped_column(String(10))  # +, -, simplex
    tone: Mapped[Optional[float]] = mapped_column(Numeric(6, 1))
    tone_type: Mapped[str] = mapped_column(String(10), default="none")  # none/ctcss/dcs
    dcs_code: Mapped[Optional[str]] = mapped_column(String(10))
    bandwidth: Mapped[str] = mapped_column(String(10), default="narrow")  # narrow/wide
    mode: Mapped[str] = mapped_column(String(10), default="fm")  # fm/dmr/c4fm/dstar/nxdn/m17
    duplex: Mapped[str] = mapped_column(String(10), default="simplex")  # simplex/minus/plus
    power: Mapped[Optional[float]] = mapped_column(Float)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    altitude: Mapped[Optional[float]] = mapped_column(Float)
    coverage_radius: Mapped[Optional[float]] = mapped_column(Float)
    state_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("states.id"))
    country: Mapped[str] = mapped_column(String(50), default="Malaysia")
    category: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/inactive/testing
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    state_rel: Mapped[Optional["State"]] = relationship(back_populates="repeaters")

    def __repr__(self) -> str:
        return f"<Repeater {self.callsign or self.name} @ {self.rx_freq}>"


class SimplexChannel(Base):
    __tablename__ = "simplex_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    tx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    tone: Mapped[Optional[float]] = mapped_column(Numeric(6, 1))
    tone_type: Mapped[str] = mapped_column(String(10), default="none")
    bandwidth: Mapped[str] = mapped_column(String(10), default="narrow")
    mode: Mapped[str] = mapped_column(String(10), default="fm")
    power: Mapped[Optional[float]] = mapped_column(Float)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<SimplexChannel {self.name}>"


class MarineChannel(Base):
    __tablename__ = "marine_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_num: Mapped[Optional[str]] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    tx_freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    mode: Mapped[str] = mapped_column(String(10), default="fm")
    power: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<MarineChannel {self.channel_num}: {self.name}>"


class AviationFreq(Base):
    __tablename__ = "aviation_freqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    freq: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    type: Mapped[str] = mapped_column(String(20))  # approach/tower/ground/atis/unicom
    airport: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<AviationFreq {self.name} @ {self.freq}>"


class AprsObject(Base):
    __tablename__ = "aprs_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    callsign: Mapped[str] = mapped_column(String(20), nullable=False)
    frequency: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    symbol: Mapped[Optional[str]] = mapped_column(String(10))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    altitude: Mapped[Optional[float]] = mapped_column(Float)
    type: Mapped[str] = mapped_column(String(20))  # igate/digipeater
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<AprsObject {self.callsign}>"


class Satellite(Base):
    __tablename__ = "satellites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    norad_id: Mapped[Optional[int]] = mapped_column(Integer)
    uplink: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    downlink: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    beacon: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Satellite {self.name}>"


class EmergencyFreq(Base):
    __tablename__ = "emergency_freqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    agency: Mapped[Optional[str]] = mapped_column(String(100))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<EmergencyFreq {self.name}>"


class CallingFreq(Base):
    __tablename__ = "calling_freqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    band: Mapped[Optional[str]] = mapped_column(String(20))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<CallingFreq {self.name}>"
