from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Numeric
from app.database import Base


class UrbansenseSound(Base):
    """Minute-level sound readings at BTS stations."""
    __tablename__ = "urbansense_s"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    station_id = Column(String(50), nullable=False, index=True)
    min_db = Column(Float, nullable=False)
    max_db = Column(Float, nullable=False)
    peak_db = Column(Float, nullable=False)
    avg_db = Column(Float, nullable=False)


class UrbansenseTempHumid(Base):
    """Minute-level temperature & humidity readings at BTS stations."""
    __tablename__ = "urbansense_t_h"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    station_id = Column(String(50), nullable=False, index=True)
    temp = Column(Float, nullable=False)
    humid = Column(Float, nullable=False)
    is_rush_hour = Column(Boolean, nullable=False)


class WeatherSiam(Base):
    """Daily weather data for the BTS-Siam station area."""
    __tablename__ = "weather_siam"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    station = Column(String(50), nullable=False)
    latitude = Column(Numeric(10, 6), nullable=False)
    longitude = Column(Numeric(10, 6), nullable=False)
    elevation = Column(Numeric(5, 1), nullable=False)
    temperature_2m_mean = Column(Numeric(4, 1))
    temperature_2m_max = Column(Numeric(4, 1))
    temperature_2m_min = Column(Numeric(4, 1))
    apparent_temperature_mean = Column(Numeric(4, 1))
    apparent_temperature_max = Column(Numeric(4, 1))
    apparent_temperature_min = Column(Numeric(4, 1))
    relative_humidity_2m_max = Column(Integer)
    relative_humidity_2m_min = Column(Integer)
    rain_sum = Column(Numeric(5, 2))


class WeatherLadprow(Base):
    """Daily weather data for the BTS-Ladprao station area."""
    __tablename__ = "weather_ladprow"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    station = Column(String(50), nullable=False)
    latitude = Column(Numeric(10, 6), nullable=False)
    longitude = Column(Numeric(10, 6), nullable=False)
    elevation = Column(Numeric(5, 1), nullable=False)
    temperature_2m_mean = Column(Numeric(4, 1))
    temperature_2m_max = Column(Numeric(4, 1))
    temperature_2m_min = Column(Numeric(4, 1))
    apparent_temperature_mean = Column(Numeric(4, 1))
    apparent_temperature_max = Column(Numeric(4, 1))
    apparent_temperature_min = Column(Numeric(4, 1))
    relative_humidity_2m_max = Column(Integer)
    relative_humidity_2m_min = Column(Integer)
    rain_sum = Column(Numeric(5, 2))


class MrtPink(Base):
    __tablename__ = "mrt_pink"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    line = Column(String(20), nullable=False)
    population = Column(Integer, nullable=False)


class MrtBlue(Base):
    __tablename__ = "mrt_blue"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    line = Column(String(20), nullable=False)
    population = Column(Integer, nullable=False)


class MrtYellow(Base):
    __tablename__ = "mrt_yellow"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    line = Column(String(20), nullable=False)
    population = Column(Integer, nullable=False)


class MrtPurple(Base):
    __tablename__ = "mrt_purple"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    line = Column(String(20), nullable=False)
    population = Column(Integer, nullable=False)
