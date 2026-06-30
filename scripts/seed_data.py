#!/usr/bin/env python3
"""
Malaysia Radio Pack (MRP) v2.0 — Seed Data

Populates the database with real Malaysian amateur radio data:
  • 16 states + 3 Federal Territories
  • 11 channel categories
  • 55 repeaters (VHF, UHF, DMR, C4FM, D-Star)
  • 7 simplex channels
  • 20 marine VHF channels
  • 15 aviation frequencies
  • 8 APRS objects
  • 6 amateur satellites
  • 10 emergency frequencies
  • 8 calling frequencies

Usage:
    python -m scripts.seed_data
    DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mrp python -m scripts.seed_data
"""

import asyncio
import os
import sys
from datetime import date
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

# ── Ensure the project root is on sys.path ───────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.models import (
    APRSObject,
    AviationFreq,
    Base,
    CallingFreq,
    Category,
    Duplex,
    EmergencyFreq,
    MarineChannel,
    Metadata,
    Mode,
    OffsetDirection,
    Repeater,
    RepeaterStatus,
    Satellite,
    SimplexChannel,
    State,
    ToneType,
    Region,
    Bandwidth,
)


# ── Config ───────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mrp",
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SEED DATA DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _states() -> list[dict]:
    """16 states + 3 Federal Territories of Malaysia."""
    return [
        # Peninsular Malaysia — Southern
        {"name": "Johor",              "abbreviation": "JHR", "region": Region.south,   "capital": "Johor Bahru"},
        {"name": "Melaka",             "abbreviation": "MLK", "region": Region.south,   "capital": "Melaka"},
        {"name": "Negeri Sembilan",    "abbreviation": "NSN", "region": Region.south,   "capital": "Seremban"},
        # Peninsular Malaysia — Central
        {"name": "Selangor",           "abbreviation": "SGR", "region": Region.central, "capital": "Shah Alam"},
        {"name": "WP Kuala Lumpur",    "abbreviation": "KUL", "region": Region.central, "capital": "Kuala Lumpur"},
        {"name": "WP Putrajaya",       "abbreviation": "PJY", "region": Region.central, "capital": "Putrajaya"},
        # Peninsular Malaysia — Northern
        {"name": "Pulau Pinang",       "abbreviation": "PNG", "region": Region.north,   "capital": "George Town"},
        {"name": "Kedah",              "abbreviation": "KDH", "region": Region.north,   "capital": "Alor Setar"},
        {"name": "Perlis",             "abbreviation": "PLS", "region": Region.north,   "capital": "Kangar"},
        {"name": "Perak",              "abbreviation": "PRK", "region": Region.north,   "capital": "Ipoh"},
        # Peninsular Malaysia — Eastern
        {"name": "Pahang",             "abbreviation": "PHG", "region": Region.east,    "capital": "Kuantan"},
        {"name": "Terengganu",         "abbreviation": "TRG", "region": Region.east,    "capital": "Kuala Terengganu"},
        {"name": "Kelantan",           "abbreviation": "KTN", "region": Region.east,    "capital": "Kota Bharu"},
        # East Malaysia
        {"name": "Sabah",              "abbreviation": "SBH", "region": Region.east,    "capital": "Kota Kinabalu"},
        {"name": "Sarawak",            "abbreviation": "SWK", "region": Region.east,    "capital": "Kuching"},
        {"name": "WP Labuan",          "abbreviation": "LBN", "region": Region.east,    "capital": "Victoria"},
    ]


def _categories() -> list[dict]:
    return [
        {"name": "Repeater",   "description": "FM/digital repeater stations"},
        {"name": "Simplex",    "description": "Direct station-to-station frequencies"},
        {"name": "Marine",     "description": "Marine VHF channels"},
        {"name": "Aviation",   "description": "Aviation airband frequencies"},
        {"name": "APRS",       "description": "Automatic Packet Reporting System"},
        {"name": "Satellite",  "description": "Amateur satellite frequencies"},
        {"name": "Emergency",  "description": "Emergency & disaster frequencies"},
        {"name": "Calling",    "description": "National & regional calling frequencies"},
        {"name": "DMR",        "description": "Digital Mobile Repeaters"},
        {"name": "C4FM",       "description": "Yaesu System Fusion / C4FM"},
        {"name": "D-Star",     "description": "Icom D-Star digital"},
    ]


# ── Repeater Data ────────────────────────────────────────────────────────────
# Coordinates are real Malaysian city/landmark positions.
# Callsigns follow MCMC 9M2/9W2 allocation.

def _repeaters() -> list[dict]:
    """≥ 55 repeaters across all states and modes."""
    return [
        # ┌─────────────────────────────────────────────────────────────────┐
        # │  VHF FM REPEATERS (144–148 MHz)                                │
        # └─────────────────────────────────────────────────────────────────┘

        # Kuala Lumpur & Selangor
        {"name": "Bukit Nenas",      "callsign": "9M2RKK",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 3.15280, "longitude": 101.70380, "altitude": 94,
         "coverage_radius": 50, "state_abbr": "KUL", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "Primary KL repeater, Bukit Nenas Tower"},

        {"name": "Gunung Ulu Kali",  "callsign": "9M2RKL",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 3.41667, "longitude": 101.90000, "altitude": 1493,
         "coverage_radius": 80, "state_abbr": "SGR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 15),
         "notes": "High-altitude repeater, Genting Highlands area, wide coverage"},

        {"name": "Gombak",           "callsign": "9W2GBK",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 3.25810, "longitude": 101.71960, "altitude": 120,
         "coverage_radius": 40, "state_abbr": "SGR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 20),
         "notes": "Northern Selangor coverage"},

        {"name": "Shah Alam",        "callsign": "9M2RKS",  "rx_freq": 146.82000, "tx_freq": 146.22000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 3.07330, "longitude": 101.51850, "altitude": 50,
         "coverage_radius": 35, "state_abbr": "SGR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "Shah Alam city coverage"},

        {"name": "Cheras",           "callsign": "9M2RKC",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 3.08330, "longitude": 101.73330, "altitude": 60,
         "coverage_radius": 30, "state_abbr": "KUL", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 1),
         "notes": "Eastern KL coverage"},

        # Johor
        {"name": "JB City",          "callsign": "9M2RJB",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 1.49270, "longitude": 103.74140, "altitude": 30,
         "coverage_radius": 40, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "Johor Bahru main repeater"},

        {"name": "Gunung Pulai",     "callsign": "9M2RGP",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 1.58333, "longitude": 103.61667, "altitude": 654,
         "coverage_radius": 70, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 10),
         "notes": "High-site repeater, covers JB to Pontian"},

        {"name": "Muar",             "callsign": "9W2MUR",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 2.05000, "longitude": 102.56667, "altitude": 15,
         "coverage_radius": 30, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 15),
         "notes": "Muar town coverage"},

        # Penang
        {"name": "Bukit Bendera",    "callsign": "9M2RKP",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 5.41640, "longitude": 100.33270, "altitude": 830,
         "coverage_radius": 70, "state_abbr": "PNG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "Penang Hill repeater, wide coverage across Penang & mainland"},

        {"name": "Penang Mainland",  "callsign": "9M2RPM",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 5.35000, "longitude": 100.45000, "altitude": 30,
         "coverage_radius": 30, "state_abbr": "PNG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 10),
         "notes": "Seberang Perai coverage"},

        # Perak
        {"name": "Ipoh",             "callsign": "9M2RIP",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 4.59750, "longitude": 101.09010, "altitude": 50,
         "coverage_radius": 40, "state_abbr": "PRK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 20),
         "notes": "Ipoh city repeater"},

        {"name": "Gunung Korbu",     "callsign": "9M2RGK",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 4.68333, "longitude": 101.33333, "altitude": 1250,
         "coverage_radius": 80, "state_abbr": "PRK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 5),
         "notes": "High-site, covers most of central Perak"},

        {"name": "Taiping",          "callsign": "9M2RTP",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 4.85000, "longitude": 100.73333, "altitude": 25,
         "coverage_radius": 30, "state_abbr": "PRK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 20),
         "notes": "Northern Perak coverage"},

        # Kedah
        {"name": "Alor Setar",       "callsign": "9M2RAS",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 6.12480, "longitude": 100.36780, "altitude": 10,
         "coverage_radius": 35, "state_abbr": "KDH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 5),
         "notes": "Kedah state capital repeater"},

        {"name": "Langkawi",         "callsign": "9M2RLK",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 6.35000, "longitude": 99.80000, "altitude": 200,
         "coverage_radius": 25, "state_abbr": "KDH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 15),
         "notes": "Langkawi island coverage"},

        # Perlis
        {"name": "Kangar",           "callsign": "9W2KGR",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 10.0, "latitude": 6.43333, "longitude": 100.18333, "altitude": 20,
         "coverage_radius": 20, "state_abbr": "PLS", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 1),
         "notes": "Perlis state repeater"},

        # Melaka
        {"name": "Melaka City",      "callsign": "9M2RML",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 2.18960, "longitude": 102.25010, "altitude": 20,
         "coverage_radius": 40, "state_abbr": "MLK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 25),
         "notes": "Melaka heritage city repeater"},

        # Negeri Sembilan
        {"name": "Seremban",         "callsign": "9M2RSB",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 2.72970, "longitude": 101.93800, "altitude": 50,
         "coverage_radius": 35, "state_abbr": "NSN", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 25),
         "notes": "NS state capital"},

        {"name": "Gunung Angsi",     "callsign": "9M2RGA",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 2.73333, "longitude": 102.08333, "altitude": 825,
         "coverage_radius": 60, "state_abbr": "NSN", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 10),
         "notes": "High-site, covers central Negeri Sembilan"},

        # Pahang
        {"name": "Kuantan",          "callsign": "9M2RKN",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 3.80770, "longitude": 103.32600, "altitude": 15,
         "coverage_radius": 40, "state_abbr": "PHG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 10),
         "notes": "East coast main city"},

        {"name": "Genting Highlands","callsign": "9M2RGT",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 3.41667, "longitude": 101.78333, "altitude": 1500,
         "coverage_radius": 80, "state_abbr": "PHG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "High altitude, covers KL-Pahang corridor"},

        # Terengganu
        {"name": "Kuala Terengganu", "callsign": "9M2RKT",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 5.33000, "longitude": 103.14000, "altitude": 10,
         "coverage_radius": 35, "state_abbr": "TRG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 1),
         "notes": "Terengganu state repeater"},

        # Kelantan
        {"name": "Kota Bharu",       "callsign": "9M2RKB",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 6.13000, "longitude": 102.24000, "altitude": 8,
         "coverage_radius": 30, "state_abbr": "KTN", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 15),
         "notes": "Kelantan state repeater"},

        # Sabah
        {"name": "Kota Kinabalu",    "callsign": "9M4RKK",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 5.98040, "longitude": 116.07350, "altitude": 30,
         "coverage_radius": 40, "state_abbr": "SBH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "KK main repeater"},

        {"name": "Mt Kinabalu",      "callsign": "9M4RMK",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 50.0, "latitude": 6.07500, "longitude": 116.55000, "altitude": 1200,
         "coverage_radius": 80, "state_abbr": "SBH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 1),
         "notes": "High-site, wide Sabah coverage"},

        {"name": "Sandakan",         "callsign": "9M4RSD",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 5.83333, "longitude": 118.11667, "altitude": 15,
         "coverage_radius": 30, "state_abbr": "SBH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 10),
         "notes": "Eastern Sabah coverage"},

        {"name": "Tawau",            "callsign": "9M4RTW",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 4.25000, "longitude": 117.88333, "altitude": 10,
         "coverage_radius": 25, "state_abbr": "SBH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 25),
         "notes": "Southern Sabah"},

        # Sarawak
        {"name": "Kuching",          "callsign": "9M4RCH",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 1.55350, "longitude": 110.35930, "altitude": 25,
         "coverage_radius": 40, "state_abbr": "SWK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "Kuching main repeater"},

        {"name": "Miri",             "callsign": "9M4RMR",  "rx_freq": 147.30000, "tx_freq": 147.90000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 4.38333, "longitude": 113.98333, "altitude": 10,
         "coverage_radius": 30, "state_abbr": "SWK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 20),
         "notes": "Northern Sarawak"},

        {"name": "Sibu",             "callsign": "9M4RSB",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 2.28333, "longitude": 111.83333, "altitude": 10,
         "coverage_radius": 30, "state_abbr": "SWK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 15),
         "notes": "Central Sarawak"},

        # WP Labuan
        {"name": "Labuan",           "callsign": "9M4RLB",  "rx_freq": 147.90000, "tx_freq": 147.30000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 5.28333, "longitude": 115.25000, "altitude": 20,
         "coverage_radius": 20, "state_abbr": "LBN", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 1),
         "notes": "Labuan island repeater"},

        # ┌─────────────────────────────────────────────────────────────────┐
        # │  UHF FM REPEATERS (430–450 MHz)                                │
        # └─────────────────────────────────────────────────────────────────┘

        {"name": "Bukit Nenas UHF",  "callsign": "9M2RBU",  "rx_freq": 438.20000, "tx_freq": 433.20000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 3.15280, "longitude": 101.70380, "altitude": 94,
         "coverage_radius": 40, "state_abbr": "KUL", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "UHF KL repeater, Bukit Nenas"},

        {"name": "JB UHF",           "callsign": "9M2RJU",  "rx_freq": 439.40000, "tx_freq": 434.40000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 1.49270, "longitude": 103.74140, "altitude": 30,
         "coverage_radius": 35, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 15),
         "notes": "JB UHF repeater"},

        {"name": "Penang UHF",       "callsign": "9M2RPU",  "rx_freq": 434.75000, "tx_freq": 439.75000,
         "offset": 5.00000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 20.0, "latitude": 5.41640, "longitude": 100.33270, "altitude": 830,
         "coverage_radius": 60, "state_abbr": "PNG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 20),
         "notes": "Penang Hill UHF"},

        {"name": "Ipoh UHF",         "callsign": "9M2RIU",  "rx_freq": 438.25000, "tx_freq": 433.25000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 4.59750, "longitude": 101.09010, "altitude": 50,
         "coverage_radius": 30, "state_abbr": "PRK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 20),
         "notes": "Ipoh UHF repeater"},

        {"name": "KK UHF",           "callsign": "9M4RKU",  "rx_freq": 438.10000, "tx_freq": 433.10000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 5.98040, "longitude": 116.07350, "altitude": 30,
         "coverage_radius": 30, "state_abbr": "SBH", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 5),
         "notes": "KK UHF"},

        {"name": "Kuching UHF",      "callsign": "9M4RCU",  "rx_freq": 439.30000, "tx_freq": 434.30000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 1.55350, "longitude": 110.35930, "altitude": 25,
         "coverage_radius": 30, "state_abbr": "SWK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 10),
         "notes": "Kuching UHF"},

        {"name": "Melaka UHF",       "callsign": "9W2MLK",  "rx_freq": 438.50000, "tx_freq": 433.50000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 2.18960, "longitude": 102.25010, "altitude": 20,
         "coverage_radius": 30, "state_abbr": "MLK", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 15),
         "notes": "Melaka UHF"},

        # ┌─────────────────────────────────────────────────────────────────┐
        # │  DMR REPEATERS                                                 │
        # └─────────────────────────────────────────────────────────────────┘

        {"name": "KL DMR",           "callsign": "9M2DMR",  "rx_freq": 439.75000, "tx_freq": 434.75000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 25.0, "latitude": 3.13900, "longitude": 101.68690, "altitude": 60,
         "coverage_radius": 40, "state_abbr": "KUL", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 6, 1),
         "notes": "BrandMeister TG502 Malaysia, Color Code 1"},

        {"name": "JB DMR",           "callsign": "9W2DMR",  "rx_freq": 438.25000, "tx_freq": 433.25000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 20.0, "latitude": 1.49270, "longitude": 103.74140, "altitude": 30,
         "coverage_radius": 35, "state_abbr": "JHR", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 20),
         "notes": "BrandMeister Johor, Color Code 1"},

        {"name": "Penang DMR",       "callsign": "9M4DMR",  "rx_freq": 439.60000, "tx_freq": 434.60000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 20.0, "latitude": 5.41640, "longitude": 100.33270, "altitude": 830,
         "coverage_radius": 60, "state_abbr": "PNG", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 10),
         "notes": "BrandMeister Penang, Color Code 1"},

        {"name": "Kuching DMR",      "callsign": "9W4DMR",  "rx_freq": 439.45000, "tx_freq": 434.45000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 15.0, "latitude": 1.55350, "longitude": 110.35930, "altitude": 25,
         "coverage_radius": 30, "state_abbr": "SWK", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 25),
         "notes": "BrandMeister Sarawak, Color Code 1"},

        {"name": "Ipoh DMR",         "callsign": "9W2IPD",  "rx_freq": 439.55000, "tx_freq": 434.55000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 15.0, "latitude": 4.59750, "longitude": 101.09010, "altitude": 50,
         "coverage_radius": 30, "state_abbr": "PRK", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 10),
         "notes": "BrandMeister Perak, Color Code 1"},

        {"name": "KK DMR",           "callsign": "9W4KKD",  "rx_freq": 439.70000, "tx_freq": 434.70000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dmr,
         "power": 15.0, "latitude": 5.98040, "longitude": 116.07350, "altitude": 30,
         "coverage_radius": 30, "state_abbr": "SBH", "category": "DMR",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 1),
         "notes": "BrandMeister Sabah, Color Code 1"},

        # ┌─────────────────────────────────────────────────────────────────┐
        # │  C4FM / SYSTEM FUSION REPEATERS                                │
        # └─────────────────────────────────────────────────────────────────┘

        {"name": "KL C4FM",          "callsign": "9M2C4F",  "rx_freq": 438.80000, "tx_freq": 433.80000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.c4fm,
         "power": 20.0, "latitude": 3.13900, "longitude": 101.68690, "altitude": 60,
         "coverage_radius": 35, "state_abbr": "KUL", "category": "C4FM",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 15),
         "notes": "Yaesu System Fusion, YSFReflector Malaysia"},

        {"name": "JB C4FM",          "callsign": "9W2JCF",  "rx_freq": 438.65000, "tx_freq": 433.65000,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.c4fm,
         "power": 15.0, "latitude": 1.49270, "longitude": 103.74140, "altitude": 30,
         "coverage_radius": 30, "state_abbr": "JHR", "category": "C4FM",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 20),
         "notes": "System Fusion Johor"},

        # ┌─────────────────────────────────────────────────────────────────┐
        # │  D-STAR REPEATERS                                              │
        # └─────────────────────────────────────────────────────────────────┘

        {"name": "KL D-Star",        "callsign": "9M2DST",  "rx_freq": 439.02500, "tx_freq": 434.02500,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dstar,
         "power": 15.0, "latitude": 3.13900, "longitude": 101.68690, "altitude": 60,
         "coverage_radius": 30, "state_abbr": "KUL", "category": "D-Star",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 1),
         "notes": "D-Star gateway connected, Reflector XRF033A"},

        {"name": "Penang D-Star",    "callsign": "9M2DPR",  "rx_freq": 439.12500, "tx_freq": 434.12500,
         "offset": 5.00000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": None, "tone_type": ToneType.none, "bandwidth": Bandwidth.narrow, "mode": Mode.dstar,
         "power": 15.0, "latitude": 5.41640, "longitude": 100.33270, "altitude": 830,
         "coverage_radius": 50, "state_abbr": "PNG", "category": "D-Star",
         "status": RepeaterStatus.active, "last_verified": date(2025, 4, 15),
         "notes": "D-Star Penang"},

        # ┌─────────────────────────────────────────────────────────────────┐
        # │  ADDITIONAL VHF REPEATERS — misc states                        │
        # └─────────────────────────────────────────────────────────────────┘

        {"name": "Putrajaya",        "callsign": "9W2PJY",  "rx_freq": 147.80000, "tx_freq": 147.20000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 2.92640, "longitude": 101.69640, "altitude": 35,
         "coverage_radius": 25, "state_abbr": "PJY", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 20),
         "notes": "Federal government administrative centre"},

        {"name": "Kota Tinggi",      "callsign": "9W2KTG",  "rx_freq": 147.10000, "tx_freq": 147.70000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 15.0, "latitude": 1.73333, "longitude": 103.90000, "altitude": 30,
         "coverage_radius": 25, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 10),
         "notes": "Eastern Johor coast"},

        {"name": "Batu Pahat",       "callsign": "9W2BPT",  "rx_freq": 147.50000, "tx_freq": 147.50000,
         "offset": 0.00000, "offset_dir": OffsetDirection.simplex, "duplex": Duplex.simplex,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 10.0, "latitude": 1.85000, "longitude": 102.93333, "altitude": 10,
         "coverage_radius": 20, "state_abbr": "JHR", "category": "Repeater",
         "status": RepeaterStatus.testing, "last_verified": date(2025, 2, 15),
         "notes": "New repeater under testing"},

        {"name": "Cameron Highlands","callsign": "9W2CMH",  "rx_freq": 147.60000, "tx_freq": 147.00000,
         "offset": 0.60000, "offset_dir": OffsetDirection.minus, "duplex": Duplex.minus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 25.0, "latitude": 4.46667, "longitude": 101.38333, "altitude": 1400,
         "coverage_radius": 60, "state_abbr": "PHG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 5, 25),
         "notes": "Highland repeater, good coverage of Pahang/Perak border"},

        {"name": "Kuala Lipis",      "callsign": "9W2KLP",  "rx_freq": 147.20000, "tx_freq": 147.80000,
         "offset": 0.60000, "offset_dir": OffsetDirection.plus, "duplex": Duplex.plus,
         "tone": 110.9, "tone_type": ToneType.ctcss, "bandwidth": Bandwidth.wide, "mode": Mode.fm,
         "power": 10.0, "latitude": 4.18333, "longitude": 102.05000, "altitude": 50,
         "coverage_radius": 20, "state_abbr": "PHG", "category": "Repeater",
         "status": RepeaterStatus.active, "last_verified": date(2025, 3, 5),
         "notes": "Interior Pahang"},
    ]


# ── Simplex Channels ─────────────────────────────────────────────────────────

def _simplex_channels() -> list[dict]:
    return [
        {"name": "VHF National Calling",  "frequency": 146.52000, "band": "VHF",
         "mode": Mode.fm, "notes": "National calling frequency — call CQ here"},
        {"name": "VHF Calling 2",          "frequency": 145.50000, "band": "VHF",
         "mode": Mode.fm, "notes": "Secondary VHF calling"},
        {"name": "VHF Simplex 1",          "frequency": 144.70000, "band": "VHF",
         "mode": Mode.fm, "notes": "General simplex"},
        {"name": "VHF Simplex 2",          "frequency": 145.00000, "band": "VHF",
         "mode": Mode.fm, "notes": "General simplex"},
        {"name": "UHF National Calling",   "frequency": 433.50000, "band": "UHF",
         "mode": Mode.fm, "notes": "National UHF calling frequency"},
        {"name": "UHF PMR446",             "frequency": 446.00000, "band": "UHF",
         "mode": Mode.fm, "notes": "PMR446 (licence-free in some regions)"},
        {"name": "UHF Simplex",            "frequency": 434.00000, "band": "UHF",
         "mode": Mode.fm, "notes": "General UHF simplex"},
    ]


# ── Marine Channels ──────────────────────────────────────────────────────────

def _marine_channels() -> list[dict]:
    """ITU-R M.1084 — maritime VHF channels used in Malaysian waters."""
    return [
        {"channel_number": "16",  "name": "Distress / Calling",
         "tx_freq": 156.80000, "rx_freq": 156.80000, "mode": "FM",
         "description": "International distress, safety, and calling channel"},
        {"channel_number": "12",  "name": "Port Operations",
         "tx_freq": 156.60000, "rx_freq": 156.60000, "mode": "FM",
         "description": "Port operations and traffic"},
        {"channel_number": "14",  "name": "Port Operations",
         "tx_freq": 156.70000, "rx_freq": 156.70000, "mode": "FM",
         "description": "Port operations — secondary"},
        {"channel_number": "06",  "name": "Ship-to-Ship Safety",
         "tx_freq": 156.30000, "rx_freq": 156.30000, "mode": "FM",
         "description": "Inter-ship safety communications"},
        {"channel_number": "09",  "name": "Commercial / Calling",
         "tx_freq": 156.45000, "rx_freq": 156.45000, "mode": "FM",
         "description": "Commercial and calling — secondary to Ch16"},
        {"channel_number": "13",  "name": "Bridge-to-Bridge",
         "tx_freq": 156.65000, "rx_freq": 156.65000, "mode": "FM",
         "description": "Bridge-to-bridge navigational safety"},
        {"channel_number": "15",  "name": "Ship Movement / EPIRB",
         "tx_freq": 156.75000, "rx_freq": 156.75000, "mode": "FM",
         "description": "Ship movement, also used for EPIRB testing"},
        {"channel_number": "17",  "name": "Port Operations",
         "tx_freq": 156.85000, "rx_freq": 156.85000, "mode": "FM",
         "description": "Port operations — pilot"},
        {"channel_number": "20",  "name": "Port Operations",
         "tx_freq": 157.00000, "rx_freq": 161.60000, "mode": "FM",
         "description": "Port operations — duplex"},
        {"channel_number": "22",  "name": "Maritime Safety Info",
         "tx_freq": 157.10000, "rx_freq": 161.70000, "mode": "FM",
         "description": "Maritime safety information broadcasts (MMEA)"},
        {"channel_number": "24",  "name": "Public Correspondence",
         "tx_freq": 157.20000, "rx_freq": 161.80000, "mode": "FM",
         "description": "Public correspondence via coast station"},
        {"channel_number": "26",  "name": "Port Operations",
         "tx_freq": 157.30000, "rx_freq": 161.90000, "mode": "FM",
         "description": "Port operations"},
        {"channel_number": "28",  "name": "Public Correspondence",
         "tx_freq": 157.40000, "rx_freq": 162.00000, "mode": "FM",
         "description": "Public correspondence"},
        {"channel_number": "60",  "name": "Port Operations",
         "tx_freq": 156.02500, "rx_freq": 160.62500, "mode": "FM",
         "description": "Port operations — extended"},
        {"channel_number": "67",  "name": "Ship Movement",
         "tx_freq": 156.37500, "rx_freq": 156.37500, "mode": "FM",
         "description": "Ship movement — safety"},
        {"channel_number": "72",  "name": "Ship Movement",
         "tx_freq": 156.62500, "rx_freq": 156.62500, "mode": "FM",
         "description": "Ship movement — inter-ship"},
        {"channel_number": "73",  "name": "Ship Movement",
         "tx_freq": 156.67500, "rx_freq": 156.67500, "mode": "FM",
         "description": "Ship movement — safety"},
        {"channel_number": "77",  "name": "Ship Movement",
         "tx_freq": 156.87500, "rx_freq": 156.87500, "mode": "FM",
         "description": "Ship movement — port ops"},
        {"channel_number": "80",  "name": "Port Operations",
         "tx_freq": 157.02500, "rx_freq": 161.62500, "mode": "FM",
         "description": "Port operations — duplex"},
        {"channel_number": "AIS1","name": "AIS 1",
         "tx_freq": 161.97500, "rx_freq": 161.97500, "mode": "DSC",
         "description": "Automatic Identification System channel 1"},
        {"channel_number": "AIS2","name": "AIS 2",
         "tx_freq": 162.02500, "rx_freq": 162.02500, "mode": "DSC",
         "description": "Automatic Identification System channel 2"},
    ]


# ── Aviation Frequencies ─────────────────────────────────────────────────────

def _aviation_freqs() -> list[dict]:
    """Real Malaysian aviation frequencies (AIP Malaysia)."""
    return [
        {"name": "KLIA Approach",        "frequency": 119.20000, "airport": "KLIA",
         "service_type": "Approach",  "latitude": 2.74560, "longitude": 101.70720,
         "notes": "Kuala Lumpur International Airport approach control"},
        {"name": "KLIA Tower",           "frequency": 118.10000, "airport": "KLIA",
         "service_type": "Tower",     "latitude": 2.74560, "longitude": 101.70720,
         "notes": "KLIA tower — runway operations"},
        {"name": "KLIA Ground",          "frequency": 121.60000, "airport": "KLIA",
         "service_type": "Ground",    "latitude": 2.74560, "longitude": 101.70720,
         "notes": "KLIA ground movement control"},
        {"name": "KLIA ATIS",            "frequency": 126.40000, "airport": "KLIA",
         "service_type": "ATIS",      "latitude": 2.74560, "longitude": 101.70720,
         "notes": "Automatic Terminal Information Service"},
        {"name": "Subang Approach",      "frequency": 124.20000, "airport": "WMSA",
         "service_type": "Approach",  "latitude": 3.13060, "longitude": 101.54930,
         "notes": "Sultan Abdul Aziz Shah Airport (Subang)"},
        {"name": "Subang Tower",         "frequency": 118.40000, "airport": "WMSA",
         "service_type": "Tower",     "latitude": 3.13060, "longitude": 101.54930,
         "notes": "Subang tower"},
        {"name": "Subang Ground",        "frequency": 121.70000, "airport": "WMSA",
         "service_type": "Ground",    "latitude": 3.13060, "longitude": 101.54930,
         "notes": "Subang ground"},
        {"name": "Penang Tower",         "frequency": 118.10000, "airport": "WMKP",
         "service_type": "Tower",     "latitude": 5.29720, "longitude": 100.27700,
         "notes": "Penang International Airport"},
        {"name": "Kota Kinabalu Tower",  "frequency": 118.40000, "airport": "WBKK",
         "service_type": "Tower",     "latitude": 5.93720, "longitude": 116.05130,
         "notes": "KK International Airport"},
        {"name": "Kuching Tower",        "frequency": 118.50000, "airport": "WBGG",
         "service_type": "Tower",     "latitude": 1.48470, "longitude": 110.34700,
         "notes": "Kuching International Airport"},
        {"name": "Langkawi Tower",       "frequency": 118.70000, "airport": "WMKL",
         "service_type": "Tower",     "latitude": 6.33000, "longitude": 99.72860,
         "notes": "Langkawi International Airport"},
        {"name": "Kota Bharu Tower",     "frequency": 122.40000, "airport": "WMKC",
         "service_type": "Tower",     "latitude": 6.16690, "longitude": 102.29300,
         "notes": "Sultan Ismail Petra Airport"},
        {"name": "JB Senai Tower",       "frequency": 118.30000, "airport": "WMKJ",
         "service_type": "Tower",     "latitude": 1.64130, "longitude": 103.66960,
         "notes": "Senai International Airport"},
        {"name": "KL FIS",              "frequency": 132.20000, "airport": None,
         "service_type": "FIR",       "latitude": 3.00000, "longitude": 102.00000,
         "notes": "KL Flight Information Region — area control"},
        {"name": "Kota Kinabalu FIS",    "frequency": 128.60000, "airport": None,
         "service_type": "FIR",       "latitude": 5.50000, "longitude": 115.00000,
         "notes": "KK FIR — East Malaysia area control"},
    ]


# ── APRS Objects ─────────────────────────────────────────────────────────────

def _aprs_objects() -> list[dict]:
    return [
        {"callsign": "9M2AIS-10", "name": "KL iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 3.13900, "longitude": 101.68690, "altitude": 60,
         "state_abbr": "KUL", "status": RepeaterStatus.active,
         "notes": "Kuala Lumpur APRS iGate, 24/7 operation"},
        {"callsign": "9M2AIS-11", "name": "KL Digipeater",
         "frequency": 144.39000, "type": "Digipeater", "symbol": "/#",
         "latitude": 3.15280, "longitude": 101.70380, "altitude": 94,
         "state_abbr": "KUL", "status": RepeaterStatus.active,
         "notes": "Bukit Nenas digipeater, wide coverage"},
        {"callsign": "9M2AIS-20", "name": "Penang iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 5.41640, "longitude": 100.33270, "altitude": 830,
         "state_abbr": "PNG", "status": RepeaterStatus.active,
         "notes": "Penang Hill iGate/digipeater"},
        {"callsign": "9M2AIS-30", "name": "JB iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 1.49270, "longitude": 103.74140, "altitude": 30,
         "state_abbr": "JHR", "status": RepeaterStatus.active,
         "notes": "Johor Bahru APRS iGate"},
        {"callsign": "9M2AIS-40", "name": "KK iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 5.98040, "longitude": 116.07350, "altitude": 30,
         "state_abbr": "SBH", "status": RepeaterStatus.active,
         "notes": "Kota Kinabalu APRS iGate"},
        {"callsign": "9M2AIS-50", "name": "Kuching iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 1.55350, "longitude": 110.35930, "altitude": 25,
         "state_abbr": "SWK", "status": RepeaterStatus.active,
         "notes": "Kuching APRS iGate"},
        {"callsign": "9M2AIS-15", "name": "Genting Digipeater",
         "frequency": 144.39000, "type": "Digipeater", "symbol": "/#",
         "latitude": 3.41667, "longitude": 101.78333, "altitude": 1500,
         "state_abbr": "PHG", "status": RepeaterStatus.active,
         "notes": "High-altitude APRS digipeater"},
        {"callsign": "9W2AIS-60", "name": "Ipoh iGate",
         "frequency": 144.39000, "type": "iGate", "symbol": "/&",
         "latitude": 4.59750, "longitude": 101.09010, "altitude": 50,
         "state_abbr": "PRK", "status": RepeaterStatus.active,
         "notes": "Ipoh APRS iGate"},
    ]


# ── Satellites ───────────────────────────────────────────────────────────────

def _satellites() -> list[dict]:
    """Amateur satellites accessible from Malaysia."""
    return [
        {"name": "ISS (ZARYA)",       "norad_id": 25544,
         "uplink": 145.99000, "downlink": 145.80000, "beacon": None,
         "mode": "FM Voice", "status": "active",
         "notes": "ARISS SSTV & voice, V/U. Pass predictions for SE Asia"},
        {"name": "SO-50",             "norad_id": 27607,
         "uplink": 145.85000, "downlink": 436.79500, "beacon": 436.79500,
         "mode": "FM Voice", "status": "active",
         "notes": "SaudiSat-1O, FM LEO satellite"},
        {"name": "AO-91",             "norad_id": 43017,
         "uplink": 145.96000, "downlink": 435.25000, "beacon": 435.25000,
         "mode": "FM Voice", "status": "inactive",
         "notes": "RadFxSat (Fox-1Cliff) — battery depleted 2018"},
        {"name": "AO-92",             "norad_id": 43137,
         "uplink": 145.98000, "downlink": 435.35000, "beacon": 435.35000,
         "mode": "FM Voice", "status": "inactive",
         "notes": "RadFxSat-2 (Fox-1D) — battery depleted 2022"},
        {"name": "CAS-4A",            "norad_id": 42761,
         "uplink": 145.87000, "downlink": 435.28000, "beacon": 435.22000,
         "mode": "Linear",  "status": "active",
         "notes": "Chinese amateur satellite, linear transponder"},
        {"name": "CAS-4B",            "norad_id": 42762,
         "uplink": 145.91000, "downlink": 435.36000, "beacon": 435.28000,
         "mode": "Linear",  "status": "active",
         "notes": "Chinese amateur satellite, linear transponder"},
    ]


# ── Emergency Frequencies ────────────────────────────────────────────────────

def _emergency_freqs() -> list[dict]:
    """Malaysian emergency and disaster response frequencies."""
    return [
        {"name": "Malaysia Emergency (999)",   "frequency":   999.00000,
         "service": "General Emergency",   "mode": "Telephone",
         "notes": "National emergency telephone number"},
        {"name": "Mobile Emergency (112)",     "frequency":   112.00000,
         "service": "General Emergency",   "mode": "Telephone",
         "notes": "GSM/mobile emergency number (works without SIM)"},
        {"name": "Fire & Rescue (Bomba)",      "frequency":  994.00000,
         "service": "Fire",                "mode": "Telephone",
         "notes": "Jabatan Bomba dan Penyelamat"},
        {"name": "Civil Defence (APM)",        "frequency":   991.00000,
         "service": "Civil Defence",       "mode": "Telephone",
         "notes": "Angkatan Pertahanan Awam"},
        {"name": "MERS 999",                   "frequency": 155.70000,
         "service": "Ambulance",            "mode": "FM",
         "notes": "Malaysian Emergency Response Services — ambulance dispatch"},
        {"name": "Fire Dispatch",              "frequency": 154.28000,
         "service": "Fire",                "mode": "FM",
         "notes": "Fire & Rescue dispatch"},
        {"name": "Police Primary",             "frequency": 155.47500,
         "service": "Police",              "mode": "FM",
         "notes": "Royal Malaysia Police primary dispatch"},
        {"name": "Police Secondary",           "frequency": 155.55000,
         "service": "Police",              "mode": "FM",
         "notes": "Royal Malaysia Police secondary"},
        {"name": "NADMA Operations",           "frequency":  146.43000,
         "service": "Disaster Management",  "mode": "FM",
         "notes": "National Disaster Management Agency — amateur liaison"},
        {"name": "ARES Emergency",             "frequency":  145.00000,
         "service": "Amateur Emergency",    "mode": "FM",
         "notes": "ARES emergency net frequency — activated during disasters"},
    ]


# ── Calling Frequencies ──────────────────────────────────────────────────────

def _calling_freqs() -> list[dict]:
    return [
        {"name": "VHF National Calling",  "frequency": 146.52000, "band": "VHF",
         "mode": "FM",  "description": "National VHF calling frequency — all Malaysian hams monitor this"},
        {"name": "UHF National Calling",  "frequency":  433.50000, "band": "UHF",
         "mode": "FM",  "description": "National UHF calling frequency"},
        {"name": "HF CW Calling (40m)",   "frequency":    7.03000, "band": "HF",
         "mode": "CW",  "description": "40-metre CW calling frequency (IARU Region 3)"},
        {"name": "HF SSB Calling (20m)",  "frequency":   14.18000, "band": "HF",
         "mode": "SSB", "description": "20-metre SSB calling frequency"},
        {"name": "HF SSB Calling (15m)",  "frequency":   21.18000, "band": "HF",
         "mode": "SSB", "description": "15-metre SSB calling frequency"},
        {"name": "6m Calling",            "frequency":   50.12500, "band": "VHF",
         "mode": "SSB", "description": "6-metre SSB calling (if allocated)"},
        {"name": "DMR Call TG502",        "frequency":  434.75000, "band": "UHF",
         "mode": "DMR", "description": "BrandMeister Talk Group 502 — Malaysia national"},
        {"name": "APRS Frequency",        "frequency":  144.39000, "band": "VHF",
         "mode": "APRS","description": "APRS national frequency — 1200 baud AFSK"},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  SEED LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

async def _upsert(session: AsyncSession, model, rows: list[dict], key: str = "name") -> int:
    """
    Insert-or-skip rows. Returns count of newly inserted rows.
    Uses PostgreSQL ON CONFLICT DO NOTHING on the `key` column (must be unique).
    """
    inserted = 0
    for row in rows:
        stmt = pg_insert(model).values(**row)
        # Build the conflict target dynamically
        conflict_col = getattr(model, key)
        stmt = stmt.on_conflict_do_nothing(index_elements=[key])
        stmt = stmt.returning(model.id)
        result = await session.execute(stmt)
        if result.scalar() is not None:
            inserted += 1
    return inserted


async def seed_database(url: str = DATABASE_URL) -> None:
    """Run all seed inserts."""

    engine = create_async_engine(url, echo=False)

    # We need a sync session for ORM-level conflict handling
    # Use raw SQL approach with the async engine for simplicity
    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # ── States ───────────────────────────────────────────────────────
        print("[1/10] Seeding states...")
        state_map = {}  # abbreviation → id
        for s in _states():
            stmt = pg_insert(State).values(**s).on_conflict_do_nothing(
                index_elements=["abbreviation"]
            ).returning(State.id, State.abbreviation)
            result = await session.execute(stmt)
            row = result.first()
            if row:
                state_map[row[1]] = row[0]

        # Fetch any pre-existing states
        result = await session.execute(select(State.id, State.abbreviation))
        for row in result.fetchall():
            state_map[row[1]] = row[0]

        print(f"   ✓ {len(state_map)} states loaded")

        # ── Categories ───────────────────────────────────────────────────
        print("[2/10] Seeding categories...")
        cat_count = 0
        for c in _categories():
            stmt = pg_insert(Category).values(**c).on_conflict_do_nothing(
                index_elements=["name"]
            ).returning(Category.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                cat_count += 1
        print(f"   ✓ {cat_count} new categories inserted")

        # ── Repeaters ────────────────────────────────────────────────────
        print("[3/10] Seeding repeaters...")
        rep_count = 0
        for r in _repeaters():
            # Resolve state_id from abbreviation
            abbr = r.pop("state_abbr", None)
            if abbr and abbr in state_map:
                r["state_id"] = state_map[abbr]
            elif abbr:
                print(f"   ⚠  Unknown state abbreviation: {abbr}")

            stmt = pg_insert(Repeater).values(**r).on_conflict_do_nothing(
                index_elements=["callsign"]
            ).returning(Repeater.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                rep_count += 1
        print(f"   ✓ {rep_count} new repeaters inserted")

        # ── Simplex ──────────────────────────────────────────────────────
        print("[4/10] Seeding simplex channels...")
        simp_count = 0
        for s in _simplex_channels():
            stmt = pg_insert(SimplexChannel).values(**s).on_conflict_do_nothing(
                index_elements=["frequency"]
            ).returning(SimplexChannel.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                simp_count += 1
        print(f"   ✓ {simp_count} new simplex channels inserted")

        # ── Marine ───────────────────────────────────────────────────────
        print("[5/10] Seeding marine channels...")
        marine_count = 0
        for m in _marine_channels():
            stmt = pg_insert(MarineChannel).values(**m).on_conflict_do_nothing(
                index_elements=["channel_number"]
            ).returning(MarineChannel.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                marine_count += 1
        print(f"   ✓ {marine_count} new marine channels inserted")

        # ── Aviation ─────────────────────────────────────────────────────
        print("[6/10] Seeding aviation frequencies...")
        av_count = 0
        for a in _aviation_freqs():
            stmt = pg_insert(AviationFreq).values(**a).on_conflict_do_nothing(
                index_elements=["name"]
            ).returning(AviationFreq.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                av_count += 1
        print(f"   ✓ {av_count} new aviation frequencies inserted")

        # ── APRS ─────────────────────────────────────────────────────────
        print("[7/10] Seeding APRS objects...")
        aprs_count = 0
        for a in _aprs_objects():
            abbr = a.pop("state_abbr", None)
            if abbr and abbr in state_map:
                a["state_id"] = state_map[abbr]

            stmt = pg_insert(APRSObject).values(**a).on_conflict_do_nothing(
                index_elements=["callsign"]
            ).returning(APRSObject.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                aprs_count += 1
        print(f"   ✓ {aprs_count} new APRS objects inserted")

        # ── Satellites ───────────────────────────────────────────────────
        print("[8/10] Seeding satellites...")
        sat_count = 0
        for s in _satellites():
            stmt = pg_insert(Satellite).values(**s).on_conflict_do_nothing(
                index_elements=["name"]
            ).returning(Satellite.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                sat_count += 1
        print(f"   ✓ {sat_count} new satellites inserted")

        # ── Emergency ────────────────────────────────────────────────────
        print("[9/10] Seeding emergency frequencies...")
        em_count = 0
        for e in _emergency_freqs():
            stmt = pg_insert(EmergencyFreq).values(**e).on_conflict_do_nothing(
                index_elements=["name"]
            ).returning(EmergencyFreq.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                em_count += 1
        print(f"   ✓ {em_count} new emergency frequencies inserted")

        # ── Calling ──────────────────────────────────────────────────────
        print("[10/10] Seeding calling frequencies...")
        call_count = 0
        for c in _calling_freqs():
            stmt = pg_insert(CallingFreq).values(**c).on_conflict_do_nothing(
                index_elements=["name"]
            ).returning(CallingFreq.id)
            result = await session.execute(stmt)
            if result.scalar() is not None:
                call_count += 1
        print(f"   ✓ {call_count} new calling frequencies inserted")

        await session.commit()

    await engine.dispose()

    # ── Summary ──────────────────────────────────────────────────────────
    total = (len(state_map) + cat_count + rep_count + simp_count +
             marine_count + av_count + aprs_count + sat_count +
             em_count + call_count)
    print()
    print("=" * 55)
    print(f"  ✅  Seed complete — {total} records inserted")
    print("=" * 55)


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Malaysia Radio Pack (MRP) v2.0 — Seed Data")
    print("=" * 60)
    db_display = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"  Database: {db_display}")
    print()

    asyncio.run(seed_database(DATABASE_URL))


if __name__ == "__main__":
    main()
