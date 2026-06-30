"""
Malaysia Radio Pack (MRP) v2.0 — SQLAlchemy Models

Database schema for all MRP tables including PostGIS spatial columns.
"""

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship

import uuid


# ── Enums ────────────────────────────────────────────────────────────────────

class OffsetDirection(enum.Enum):
    plus = "+"
    minus = "-"
    simplex = "simplex"


class ToneType(enum.Enum):
    none = "none"
    ctcss = "ctcss"
    dcs = "dcs"


class Bandwidth(enum.Enum):
    narrow = "narrow"
    wide = "wide"


class Mode(enum.Enum):
    fm = "fm"
    dmr = "dmr"
    c4fm = "c4fm"
    dstar = "dstar"
    nxdn = "nxdn"
    m17 = "m17"


class Duplex(enum.Enum):
    simplex = "simplex"
    minus = "minus"
    plus = "plus"


class RepeaterStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    testing = "testing"


class Region(enum.Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"
    central = "central"


# ── Base ─────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── States ───────────────────────────────────────────────────────────────────

class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(10), nullable=False, unique=True)
    region = Column(Enum(Region), nullable=False)
    capital = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())

    repeaters = relationship("Repeater", back_populates="state_rel")

    def __repr__(self):
        return f"<State {self.abbreviation}: {self.name}>"


# ── Categories ───────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Category {self.name}>"


# ── Repeaters ────────────────────────────────────────────────────────────────

class Repeater(Base):
    __tablename__ = "repeaters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    callsign = Column(String(20), nullable=False, unique=True)
    rx_freq = Column(Numeric(10, 5), nullable=False)
    tx_freq = Column(Numeric(10, 5), nullable=False)
    offset = Column(Numeric(8, 5))
    offset_dir = Column(Enum(OffsetDirection), default=OffsetDirection.simplex)
    tone = Column(Numeric(5, 1))
    tone_type = Column(Enum(ToneType), default=ToneType.none)
    dcs_code = Column(Integer)
    bandwidth = Column(Enum(Bandwidth), default=Bandwidth.wide)
    mode = Column(Enum(Mode), default=Mode.fm)
    duplex = Column(Enum(Duplex), default=Duplex.simplex)
    power = Column(Numeric(6, 2))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    altitude = Column(Integer)
    coverage_radius = Column(Integer)
    state_id = Column(Integer, ForeignKey("states.id"))
    country = Column(String(3), default="MYS")
    category = Column(String(50))
    status = Column(Enum(RepeaterStatus), default=RepeaterStatus.active)
    last_verified = Column(Date)
    source = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    state_rel = relationship("State", back_populates="repeaters")

    def __repr__(self):
        return f"<Repeater {self.callsign}: {self.name}>"


# ── Simplex Channels ─────────────────────────────────────────────────────────

class SimplexChannel(Base):
    __tablename__ = "simplex_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    frequency = Column(Numeric(10, 5), nullable=False, unique=True)
    band = Column(String(10))  # VHF / UHF
    mode = Column(Enum(Mode), default=Mode.fm)
    tone = Column(Numeric(5, 1))
    tone_type = Column(Enum(ToneType), default=ToneType.none)
    power = Column(Numeric(6, 2))
    notes = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Simplex {self.name}: {self.frequency}>"


# ── Marine Channels ──────────────────────────────────────────────────────────

class MarineChannel(Base):
    __tablename__ = "marine_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_number = Column(String(10), nullable=False, unique=True)
    name = Column(String(100))
    tx_freq = Column(Numeric(10, 5), nullable=False)
    rx_freq = Column(Numeric(10, 5))
    mode = Column(String(20), default="FM")
    description = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Marine {self.channel_number}: {self.name}>"


# ── Aviation Frequencies ─────────────────────────────────────────────────────

class AviationFreq(Base):
    __tablename__ = "aviation_freqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    frequency = Column(Numeric(10, 5), nullable=False, unique=False)
    airport = Column(String(100))
    service_type = Column(String(50))  # Approach, Tower, Ground, ATIS, etc.
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    notes = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Aviation {self.name}: {self.frequency}>"


# ── APRS Objects ─────────────────────────────────────────────────────────────

class APRSObject(Base):
    __tablename__ = "aprs_objects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    callsign = Column(String(20), nullable=False, unique=True)
    name = Column(String(100))
    frequency = Column(Numeric(10, 5), default=144.39000)
    type = Column(String(30))  # iGate, Digipeater, Tracker
    symbol = Column(String(10))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    altitude = Column(Integer)
    state_id = Column(Integer, ForeignKey("states.id"))
    status = Column(Enum(RepeaterStatus), default=RepeaterStatus.active)
    notes = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<APRS {self.callsign}: {self.name}>"


# ── Satellites ───────────────────────────────────────────────────────────────

class Satellite(Base):
    __tablename__ = "satellites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    norad_id = Column(Integer, unique=True)
    uplink = Column(Numeric(10, 5))
    downlink = Column(Numeric(10, 5))
    beacon = Column(Numeric(10, 5))
    mode = Column(String(20))
    status = Column(String(20))  # active, inactive, decayed
    notes = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Satellite {self.name}>"


# ── Emergency Frequencies ────────────────────────────────────────────────────

class EmergencyFreq(Base):
    __tablename__ = "emergency_freqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    frequency = Column(Numeric(10, 5), nullable=False, unique=False)
    service = Column(String(50))  # Police, Fire, Ambulance, etc.
    mode = Column(String(20), default="FM")
    notes = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Emergency {self.name}: {self.frequency}>"


# ── Calling Frequencies ──────────────────────────────────────────────────────

class CallingFreq(Base):
    __tablename__ = "calling_freqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    frequency = Column(Numeric(10, 5), nullable=False, unique=False)
    band = Column(String(10))  # VHF, UHF, HF
    mode = Column(String(20))
    description = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Calling {self.name}: {self.frequency}>"


# ── Metadata ─────────────────────────────────────────────────────────────────

class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(String(50))
    field = Column(String(50))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(100))
    source = Column(String(200))
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100))
    verified_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Metadata {self.table_name}.{self.field}>"
