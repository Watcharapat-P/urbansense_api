from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app import models


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int((len(ordered) - 1) * p)
    return float(ordered[index])


def _summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "min": 0.0,
            "p25": 0.0,
            "p50": 0.0,
            "p75": 0.0,
            "p90": 0.0,
            "max": 0.0,
        }

    return {
        "min": float(min(values)),
        "p25": _percentile(values, 0.25),
        "p50": _percentile(values, 0.50),
        "p75": _percentile(values, 0.75),
        "p90": _percentile(values, 0.90),
        "max": float(max(values)),
    }


def _score_from_distribution(value: float, stats: dict[str, float]) -> float:
    low = stats["p25"]
    high = stats["p90"]
    if high <= low:
        ceiling = stats["max"] if stats["max"] > stats["min"] else low + 1.0
        return _clamp((value - stats["min"]) / (ceiling - stats["min"]))
    return _clamp((value - low) / (high - low))


def _range_membership(value: float, stats: dict[str, float]) -> float:
    if stats["max"] <= stats["min"]:
        return 1.0
    if stats["min"] <= value <= stats["max"]:
        return 1.0

    distance = min(abs(value - stats["min"]), abs(value - stats["max"]))
    span = stats["max"] - stats["min"]
    return _clamp(1.0 - (distance / max(span, 1.0)))


def _baseline_values(db: Session, station_id: Optional[str] = None) -> dict[str, Any]:
    sound_query = db.query(models.UrbansenseSound.avg_db)
    temp_humid_query = db.query(
        models.UrbansenseTempHumid.temp,
        models.UrbansenseTempHumid.humid,
    )

    if station_id:
        sound_query = sound_query.filter(models.UrbansenseSound.station_id == station_id)
        temp_humid_query = temp_humid_query.filter(models.UrbansenseTempHumid.station_id == station_id)

    sound_values = [float(row[0]) for row in sound_query.all() if row[0] is not None]
    temp_humid_rows = temp_humid_query.all()
    temp_values = [float(row[0]) for row in temp_humid_rows if row[0] is not None]
    humid_values = [float(row[1]) for row in temp_humid_rows if row[1] is not None]

    sample_size = min(len(sound_values), len(temp_values), len(humid_values))
    if station_id and sample_size < 10:
        return _baseline_values(db)

    return {
        "scope": station_id or "global",
        "sample_size": sample_size,
        "sound": _summarize(sound_values),
        "temp": _summarize(temp_values),
        "humid": _summarize(humid_values),
    }


def estimate_crowd_density(
    db: Session,
    *,
    temperature: float,
    humidity: float,
    avg_db: float,
    station_id: Optional[str] = None,
    is_rush_hour: Optional[bool] = None,
) -> dict[str, Any]:
    baseline = _baseline_values(db, station_id)

    sound_score = _score_from_distribution(avg_db, baseline["sound"])
    temp_score = _score_from_distribution(temperature, baseline["temp"])
    humid_score = _score_from_distribution(humidity, baseline["humid"])
    heat_crowding_bonus = 0.08 if temp_score > 0.6 and humid_score > 0.6 else 0.0
    rush_hour_bonus = 0.12 if is_rush_hour else 0.0

    raw_score = (
        (sound_score * 0.58)
        + (temp_score * 0.24)
        + (humid_score * 0.18)
        + heat_crowding_bonus
        + rush_hour_bonus
    )
    density_pct = round(_clamp(raw_score) * 100, 1)

    if density_pct < 35:
        level = "low"
    elif density_pct < 65:
        level = "moderate"
    elif density_pct < 85:
        level = "high"
    else:
        level = "very_high"

    range_fit = (
        _range_membership(avg_db, baseline["sound"])
        + _range_membership(temperature, baseline["temp"])
        + _range_membership(humidity, baseline["humid"])
    ) / 3.0
    confidence_score = 0.55 + (0.15 if station_id else 0.0) + (0.10 if is_rush_hour is not None else 0.0) + (0.20 * range_fit)
    confidence_pct = round(_clamp(confidence_score) * 100, 1)

    factors: list[str] = []
    if sound_score >= 0.7:
        factors.append("Sound level is high relative to the historical baseline.")
    elif sound_score <= 0.3:
        factors.append("Sound level is below the typical crowd-heavy range.")

    if temp_score >= 0.6:
        factors.append("Temperature is elevated versus historical readings.")
    if humid_score >= 0.6:
        factors.append("Humidity is elevated versus historical readings.")
    if heat_crowding_bonus > 0:
        factors.append("Temperature and humidity are both elevated, which often aligns with denser occupancy.")
    if is_rush_hour:
        factors.append("Rush-hour input increases the estimate because the historical dataset is denser in those periods.")
    if not factors:
        factors.append("Inputs are close to the lower or middle part of the historical sensor ranges.")

    return {
        "estimated_density_pct": density_pct,
        "estimated_level": level,
        "confidence_pct": confidence_pct,
        "baseline_scope": baseline["scope"],
        "sample_size": baseline["sample_size"],
        "factors": factors,
        "historical_reference": {
            "sound_avg_db": baseline["sound"],
            "temperature_c": baseline["temp"],
            "humidity_pct": baseline["humid"],
        },
    }