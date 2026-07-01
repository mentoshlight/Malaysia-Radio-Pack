# Malaysia Radio Pack (MRP) v2.0

A comprehensive amateur radio repeater and frequency database for Malaysia.

## Features

- **302+ channel records** — repeaters, simplex, marine, aviation, APRS, satellites, calling, emergency
- **Interactive map** with Leaflet + OpenStreetMap (coverage radius visualization)
- **Multi-format export** — CHIRP, Baofeng UV-5RM, Quansheng UV-K5, AnyTone CPS, JSON, CSV, YAML
- **REST API** with full CRUD, spatial queries (nearby repeater search), and filtering
- **Mobile-first dark dashboard** with real-time stats and charts
- **PostgreSQL + PostGIS** for spatial queries and coverage analysis

## Quick Start (Docker)

```bash
git clone https://github.com/mentoshlight/Malaysia-Radio-Pack.git
cd Malaysia-Radio-Pack
cp .env.example .env
docker compose up -d
```

Dashboard: http://localhost:8086
API docs: http://localhost:8085/docs

## Manual Setup

```bash
# Requirements: Python 3.11+, PostgreSQL 16+ with PostGIS, Redis 7+
pip install -r requirements.txt

# Database setup
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/mrp"
python -m scripts.init_db
python -m scripts.seed_data

# Run API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/repeaters` | List repeaters (paginated, filterable) |
| `GET /api/v1/repeaters/{id}` | Single repeater detail |
| `GET /api/v1/repeaters/nearby` | Proximity search (lat, lng, radius) |
| `GET /api/v1/simplex` | Simplex channels |
| `GET /api/v1/marine` | Marine VHF channels |
| `GET /api/v1/aviation` | Aviation frequencies |
| `GET /api/v1/aprs` | APRS objects |
| `GET /api/v1/satellites` | Amateur satellites |
| `GET /api/v1/emergency` | Emergency frequencies |
| `GET /api/v1/calling` | National calling frequencies |
| `GET /api/v1/states` | Malaysian states |
| `GET /api/v1/stats` | Database statistics |
| `GET /api/v1/export/chirp` | CHIRP CSV export |
| `GET /api/v1/export/uv5rm` | Baofeng UV-5RM export |
| `GET /api/v1/export/uvk5` | Quansheng UV-K5 export |
| `GET /api/v1/export/anytone` | AnyTone CPS export |
| `GET /api/v1/export/json` | Full JSON export |

All list/export endpoints accept: `?state=perak&mode=fm&band=vhf&category=repeater`

## Data Model

Each repeater contains:
- Frequencies (RX, TX, offset, direction)
- Modulation (mode, tone, tone type, bandwidth, duplex)
- Location (latitude, longitude, altitude, coverage radius, state)
- Metadata (callsign, status, last verified, source, notes)

## Project Structure

```
Malaysia-Radio-Pack/
├── api/              # FastAPI backend
│   ├── main.py       # App entry point
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Pydantic schemas
│   ├── config.py     # Settings
│   ├── cache.py      # Redis cache
│   └── routers/      # API endpoints
├── scripts/          # Database scripts
│   ├── init_db.py    # Create tables + PostGIS
│   └── seed_data.py  # Populate with Malaysian data
├── web/              # Frontend
│   ├── templates/    # HTML
│   └── static/       # CSS + JS
├── docker/           # Nginx config
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Roadmap (v3.0)

- DMR BrandMeister integration
- C4FM Fusion rooms
- D-Star reflectors
- M17 protocol
- AllStarLink / EchoLink nodes
- APRS iGate/digipeater live map
- HF band plan (IARU Region 3)
- Maidenhead grid calculator
- Distance & bearing tool
- Propagation tools
- Live repeater status
- User accounts & community contributions

## Contributing

PRs welcome. Add new repeaters, verify existing data, or improve the codebase.

## License

MIT License — see [LICENSE](LICENSE)
