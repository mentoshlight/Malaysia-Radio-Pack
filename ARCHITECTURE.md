# Malaysia Radio Pack (MRP) v2.0 — Architecture

## Overview

MRP is a comprehensive amateur radio repeater and frequency database for Malaysia.
It serves as the single source of truth for Malaysian radio frequencies, repeaters,
and related data — exportable to multiple radio programming formats.

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Database | PostgreSQL 16 + PostGIS 3.4 | Spatial queries, coverage radius |
| Cache | Redis 7 | API response caching |
| Backend | FastAPI (Python 3.11+) | REST API, export engine |
| Frontend | Vanilla JS + Leaflet + Tailwind | Dashboard, map, search |
| Container | Docker Compose | Orchestration |
| Tunnel | Cloudflare | Public access (mrp.zefa.my) |

## Database Schema

### Core Tables

```
repeaters          — Main repeater/channel data
simplex_channels   — Simplex frequencies (VHF/UHF)
marine_channels    — Marine VHF channels
aviation_freqs     — Aviation frequencies
aprs_objects       — APRS digipeaters/iGates
satellites         — Amateur satellite frequencies
emergency_freqs    — Emergency/disaster frequencies
calling_freqs      — National calling frequencies
states             — Malaysian states reference
categories         — Channel categories
metadata           — Data provenance & verification
```

### Repeater Fields

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(100) | Repeater name |
| callsign | VARCHAR(20) | Operator callsign |
| rx_freq | DECIMAL(10,5) | Receive frequency (MHz) |
| tx_freq | DECIMAL(10,5) | Transmit frequency (MHz) |
| offset | DECIMAL(8,5) | Offset (MHz) |
| offset_dir | ENUM | + / - / simplex |
| tone | DECIMAL(5,1) | CTCSS tone (Hz) |
| tone_type | ENUM | none / ctcss / dcs |
| dcs_code | INTEGER | DCS code (if applicable) |
| bandwidth | ENUM | narrow / wide |
| mode | ENUM | fm / dmr / c4fm / dstar / nxdn / m17 |
| duplex | ENUM | simplex / minus / plus |
| power | DECIMAL(6,2) | TX power (watts) |
| latitude | DECIMAL(10,7) | Latitude |
| longitude | DECIMAL(10,7) | Longitude |
| altitude | INTEGER | Altitude (meters ASL) |
| coverage_radius | INTEGER | Estimated coverage (km) |
| state_id | FK → states | State |
| country | VARCHAR(3) | Country code (MYS) |
| category | VARCHAR(50) | Category |
| status | ENUM | active / inactive / testing |
| last_verified | DATE | Last verification date |
| source | VARCHAR(200) | Data source URL/doc |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Record creation |
| updated_at | TIMESTAMP | Last update |

### Spatial Indexes

- GIST index on `latitude, longitude` for proximity queries
- PostGIS `geography` column for coverage radius calculations
- State boundary polygons for "repeaters in state" queries

## API Endpoints

### Repeaters
```
GET    /api/v1/repeaters              — List all (paginated, filterable)
GET    /api/v1/repeaters/{id}         — Single repeater detail
GET    /api/v1/repeaters/nearby       — Proximity search (lat, lng, radius_km)
POST   /api/v1/repeaters              — Create (admin)
PUT    /api/v1/repeaters/{id}         — Update (admin)
DELETE /api/v1/repeaters/{id}         — Delete (admin)
```

### Channels
```
GET    /api/v1/simplex                — Simplex channels
GET    /api/v1/marine                 — Marine channels
GET    /api/v1/aviation               — Aviation frequencies
GET    /api/v1/aprs                   — APRS objects
GET    /api/v1/satellites             — Satellite frequencies
GET    /api/v1/emergency              — Emergency frequencies
GET    /api/v1/calling                — Calling frequencies
```

### Reference
```
GET    /api/v1/states                 — Malaysian states
GET    /api/v1/categories             — Channel categories
GET    /api/v1/stats                  — Database statistics
```

### Export
```
GET    /api/v1/export/chirp           — CHIRP CSV format
GET    /api/v1/export/uv5rm           — Baofeng UV-5RM CSV
GET    /api/v1/export/uvk5            — Quansheng UV-K5 CSV
GET    /api/v1/export/anytone         — AnyTone CPS CSV
GET    /api/v1/export/tyt             — TYT CPS CSV
GET    /api/v1/export/icom            — Icom CSV
GET    /api/v1/export/kenwood         — Kenwood CSV
GET    /api/v1/export/yaesu           — Yaesu CSV
GET    /api/v1/export/json            — Full JSON export
GET    /api/v1/export/yaml            — YAML export
GET    /api/v1/export/csv             — Generic CSV export
```

All export endpoints accept query params: `?state=perak&mode=fm&band=vhf`

## Export Formats

### CHIRP CSV
```
Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE
```

### Baofeng UV-5RM / Quansheng UV-K5
Brand-specific CPS column order and formatting. Some require binary header.

### AnyTone CPS
Spreadsheet format with specific column headers for DMR codeplug software.

## Web UI

- Mobile-first responsive design (375px base)
- Leaflet map with OpenStreetMap tiles
- Marker clusters for dense areas
- Click repeater → popup with all details + "Export" button
- Sidebar: search, filters (state, band, mode, category)
- Dashboard: stats cards, charts (by state, by mode, by band)
- Dark theme (consistent with other ZeFa dashboards)

## Deployment

```yaml
# docker-compose.yml
services:
  db:       PostgreSQL 16 + PostGIS 3.4
  redis:    Redis 7
  api:      FastAPI (uvicorn)
  web:      Nginx (static files + reverse proxy)
```

Cloudflare tunnel: `mrp.zefa.my` → `http://127.0.0.1:8085`

## Data Pipeline

1. **Seed data** — Manual collection from MCMC, ARTS, club websites
2. **Community updates** — PR-based (GitHub) or web form
3. **Verification** — `last_verified` field, community voting
4. **Export** — On-demand, cached in Redis (5min TTL)

## Future (v3.0)

- DMR BrandMeister integration
- C4FM Fusion rooms
- D-Star reflectors
- M17 protocol
- AllStarLink nodes
- EchoLink nodes
- Winlink RMS gateways
- APRS iGate/digipeater map
- HF band plan (IARU Region 3)
- Maidenhead grid calculator
- Distance & bearing calculator
- Propagation tools (VOACAP integration)
- Live repeater status (owner-provided API)
- User accounts & contribution system
