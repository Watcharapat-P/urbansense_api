# UrbanSense API

FastAPI + SQLite backend for BTS station sensor data, daily weather, and MRT ridership.

## Setup

```bash
cd urbansense_api
pip install -r requirements.txt
```

## Seed the database

Place your four SQL dump files somewhere accessible, then run:

```bash
python seed_db.py \
  --sound       ../urbansense_s.sql \
  --temp-humid  ../urbansense_t_h.sql \
  --weather     ../weather_stations.sql \
  --mrt         ../mrt_ridership.sql
```

This creates `urbansense.db` in the current directory and loads all data.

## Run the server

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/sound` | List sound readings (`?station_id=`, `?limit=`, `?offset=`) |
| GET | `/api/v1/sound/{id}` | Single sound record |
| POST | `/api/v1/sound` | Create sound record |
| GET | `/api/v1/temp-humid` | List temp/humidity readings (`?station_id=`, `?rush_hour_only=true`) |
| GET | `/api/v1/temp-humid/{id}` | Single temp/humidity record |
| POST | `/api/v1/temp-humid` | Create temp/humidity record |
| GET | `/api/v1/weather` | Daily weather (`?date_from=`, `?date_to=`) |
| GET | `/api/v1/weather/{id}` | Single weather record |
| POST | `/api/v1/weather` | Create weather record |
| GET | `/api/v1/mrt/{line}` | MRT ridership — line: `pink`, `blue`, `yellow`, `purple` |
| POST | `/api/v1/mrt/{line}` | Create ridership record |

## Project Structure

```
urbansense_api/
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app + table creation on startup
│   ├── database.py   # SQLite engine & session
│   ├── models.py     # SQLAlchemy ORM models
│   ├── schemas.py    # Pydantic request/response schemas
│   └── routers.py    # All route handlers
├── seed_db.py        # One-time data loader from SQL dumps
├── requirements.txt
└── README.md
```
