from typing import List, Optional
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter()


# ── Urbansense Sound ──────────────────────────────────────────────────────────

@router.get("/sound", response_model=List[schemas.UrbansenseSoundRead], tags=["Sound"])
def get_sound_readings(
    station_id: Optional[str] = Query(None, description="Filter by station ID e.g. BTS-SIAM"),
    date_from: Optional[datetime] = Query(None, description="Start datetime e.g. 2026-04-16T00:00:00"),
    date_to: Optional[datetime] = Query(None, description="End datetime e.g. 2026-04-17T23:59:59"),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(models.UrbansenseSound)
    if station_id:
        q = q.filter(models.UrbansenseSound.station_id == station_id)
    if date_from:
        q = q.filter(models.UrbansenseSound.ts >= date_from)
    if date_to:
        q = q.filter(models.UrbansenseSound.ts <= date_to)
    return q.order_by(models.UrbansenseSound.ts.desc()).offset(offset).limit(limit).all()


@router.get("/sound/{record_id}", response_model=schemas.UrbansenseSoundRead, tags=["Sound"])
def get_sound_reading(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.UrbansenseSound).get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ── Urbansense Temp & Humidity ────────────────────────────────────────────────

@router.get("/temp-humid", response_model=List[schemas.UrbansenseTHRead], tags=["Temp & Humidity"])
def get_th_readings(
    station_id: Optional[str] = Query(None, description="Filter by station ID e.g. BTS-LADPRAO"),
    rush_hour_only: bool = Query(False),
    date_from: Optional[datetime] = Query(None, description="Start datetime e.g. 2026-04-16T00:00:00"),
    date_to: Optional[datetime] = Query(None, description="End datetime e.g. 2026-04-17T23:59:59"),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(models.UrbansenseTempHumid)
    if station_id:
        q = q.filter(models.UrbansenseTempHumid.station_id == station_id)
    if rush_hour_only:
        q = q.filter(models.UrbansenseTempHumid.is_rush_hour == True)
    if date_from:
        q = q.filter(models.UrbansenseTempHumid.ts >= date_from)
    if date_to:
        q = q.filter(models.UrbansenseTempHumid.ts <= date_to)
    return q.order_by(models.UrbansenseTempHumid.ts.desc()).offset(offset).limit(limit).all()


@router.get("/temp-humid/{record_id}", response_model=schemas.UrbansenseTHRead, tags=["Temp & Humidity"])
def get_th_reading(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.UrbansenseTempHumid).get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ── Weather (Siam & Ladprow) ───────────────────────────────────────────────────

WEATHER_MODEL_MAP = {
    "siam": models.WeatherSiam,
    "ladprow": models.WeatherLadprow,
}


def _get_weather_model(station: str):
    model = WEATHER_MODEL_MAP.get(station.lower())
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station}' not found. Valid: siam, ladprow",
        )
    return model


@router.get("/weather/{station}", response_model=List[schemas.WeatherSiamRead], tags=["Weather"])
def get_weather(
    station: str,
    date_from: Optional[date] = Query(None, description="Start date e.g. 2024-01-01"),
    date_to: Optional[date] = Query(None, description="End date e.g. 2024-12-31"),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    model = _get_weather_model(station)
    q = db.query(model)
    if date_from:
        q = q.filter(model.date >= date_from)
    if date_to:
        q = q.filter(model.date <= date_to)
    return q.order_by(model.date.desc()).offset(offset).limit(limit).all()


# ── MRT Ridership ─────────────────────────────────────────────────────────────

MRT_MODEL_MAP = {
    "pink": models.MrtPink,
    "blue": models.MrtBlue,
    "yellow": models.MrtYellow,
    "purple": models.MrtPurple,
}


def _get_mrt_model(line: str):
    model = MRT_MODEL_MAP.get(line.lower())
    if not model:
        raise HTTPException(status_code=404, detail=f"MRT line '{line}' not found. Valid: pink, blue, yellow, purple")
    return model


@router.get("/mrt/{line}", response_model=List[schemas.MrtRidershipRead], tags=["MRT Ridership"])
def get_mrt_ridership(
    line: str,
    date_from: Optional[date] = Query(None, description="Start date e.g. 2024-01-01"),
    date_to: Optional[date] = Query(None, description="End date e.g. 2024-12-31"),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    model = _get_mrt_model(line)
    q = db.query(model)
    if date_from:
        q = q.filter(model.date >= date_from)
    if date_to:
        q = q.filter(model.date <= date_to)
    return q.order_by(model.date.desc()).offset(offset).limit(limit).all()
