from dataclasses import dataclass
from datetime import datetime

from app.domain.soil_temperature_estimate import SoilTemperatureEstimate


@dataclass(frozen=True)
class WeatherData:
    observed_at: datetime
    temperature: float | None
    humidity: float | None
    precipitation: float | None
    wind_speed: float | None
    soil_temperature: float | None
    soil_temperature_6cm: float | None = None
    soil_temperature_18cm: float | None = None
    soil_temperature_10cm_estimate: SoilTemperatureEstimate | None = None