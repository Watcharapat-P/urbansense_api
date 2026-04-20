from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ── Urbansense Sound ──────────────────────────────────────────────────────────

class UrbansenseSoundBase(BaseModel):
    ts: datetime
    station_id: str
    min_db: float
    max_db: float
    peak_db: float
    avg_db: float

class UrbansenseSoundCreate(UrbansenseSoundBase):
    pass

class UrbansenseSoundRead(UrbansenseSoundBase):
    id: int

    class Config:
        from_attributes = True


# ── Urbansense Temp & Humidity ────────────────────────────────────────────────

class UrbansenseTHBase(BaseModel):
    ts: datetime
    station_id: str
    temp: float
    humid: float
    is_rush_hour: bool

class UrbansenseTHCreate(UrbansenseTHBase):
    pass

class UrbansenseTHRead(UrbansenseTHBase):
    id: int

    class Config:
        from_attributes = True


# ── Weather Siam ──────────────────────────────────────────────────────────────

class WeatherSiamBase(BaseModel):
    date: date
    station: str
    latitude: float
    longitude: float
    elevation: float
    temperature_2m_mean: Optional[float] = None
    temperature_2m_max: Optional[float] = None
    temperature_2m_min: Optional[float] = None
    apparent_temperature_mean: Optional[float] = None
    apparent_temperature_max: Optional[float] = None
    apparent_temperature_min: Optional[float] = None
    relative_humidity_2m_max: Optional[int] = None
    relative_humidity_2m_min: Optional[int] = None
    rain_sum: Optional[float] = None

class WeatherSiamCreate(WeatherSiamBase):
    pass

class WeatherSiamRead(WeatherSiamBase):
    id: int

    class Config:
        from_attributes = True


# ── MRT Ridership (shared shape for all lines) ────────────────────────────────

class MrtRidershipBase(BaseModel):
    date: date
    line: str
    population: int

class MrtRidershipCreate(MrtRidershipBase):
    pass

class MrtRidershipRead(MrtRidershipBase):
    id: int

    class Config:
        from_attributes = True


# ── Crowd Density Estimator ──────────────────────────────────────────────────

class CrowdDensityEstimateRequest(BaseModel):
    temperature_c: float
    humidity_pct: float
    avg_db: float
    station_id: Optional[str] = None
    is_rush_hour: Optional[bool] = None


class DistributionReference(BaseModel):
    min: float
    p25: float
    p50: float
    p75: float
    p90: float
    max: float


class CrowdDensityEstimateResponse(BaseModel):
    estimated_density_pct: float
    estimated_level: str
    confidence_pct: float
    baseline_scope: str
    sample_size: int
    factors: list[str]
    historical_reference: dict[str, DistributionReference]
