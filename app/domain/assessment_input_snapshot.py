from dataclasses import dataclass

from app.domain.daily_temperature import DailyTemperature
from app.domain.degree_days_result import DegreeDaysResult
from app.domain.soil_temperature_estimate import (
    SoilTemperatureEstimate,
)
from app.domain.weather_data import WeatherData


@dataclass(frozen=True)
class AssessmentInputSnapshot:
    current_weather: WeatherData | None = None
    soil_temperature_10cm_estimate: (
        SoilTemperatureEstimate | None
    ) = None
    degree_days_10c: DegreeDaysResult | None = None
    historical_observations: (
        tuple[DailyTemperature, ...] | None
    ) = None