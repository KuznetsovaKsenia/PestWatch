from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WeatherData:
    observed_at: datetime
    temperature: float | None
    humidity: float | None
    precipitation: float | None
    wind_speed: float | None
    soil_temperature: float | None