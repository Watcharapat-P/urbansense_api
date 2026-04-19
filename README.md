# UrbanSense API

FastAPI + SQLite backend for BTS station sensor data, daily weather, and MRT ridership.

## Setup

```bash
cd urbansense_api
pip install -r requirements.txt
```

## Seed the database

Place the SQL dump files in `data/table/`, then run:

```bash
python seed_db.py --sound data/table/urbansense_s.sql --temp-humid data/table/urbansense_t_h.sql --weather data/table/weather_stations.sql --mrt data/table/mrt_ridership.sql
```

This creates `urbansense.db` in the project root.

## Run the server

```bash
python -m uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

All endpoints are read-only (GET only).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/sound` | Sound readings — filter by `station_id`, `date_from`, `date_to` |
| GET | `/api/v1/sound/{id}` | Single sound record |
| GET | `/api/v1/temp-humid` | Temp & humidity — filter by `station_id`, `date_from`, `date_to`, `rush_hour_only` |
| GET | `/api/v1/temp-humid/{id}` | Single temp/humidity record |
| GET | `/api/v1/weather/{station}` | Daily weather — station: `siam` or `ladprow`, filter by `date_from`, `date_to` |
| GET | `/api/v1/mrt/{line}` | MRT ridership — line: `pink`, `blue`, `yellow`, `purple`, filter by `date_from`, `date_to` |

### Example requests

```
GET /api/v1/sound?station_id=BTS-SIAM&date_from=2026-04-17T00:00:00&date_to=2026-04-17T23:59:59
GET /api/v1/temp-humid?station_id=BTS-LADPRAO&rush_hour_only=true
GET /api/v1/weather/ladprow?date_from=2024-01-01&date_to=2024-03-31
GET /api/v1/mrt/pink?date_from=2024-01-01&date_to=2024-01-31
```

All routes support `limit` (max 1000, default 100) and `offset` for pagination.

## Project Structure

```
urbansense_api/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI app + table creation on startup
│   ├── database.py     # SQLite engine & session
│   ├── models.py       # SQLAlchemy ORM models
│   ├── schemas.py      # Pydantic request/response schemas
│   └── routers.py      # All route handlers
├── data/
│   └── table/
│       ├── urbansense_s.sql
│       ├── urbansense_t_h.sql
│       ├── weather_stations.sql
│       └── mrt_ridership.sql
├── seed_db.py          # One-time data loader from SQL dumps
├── requirements.txt
├── .gitignore
└── README.md
```
