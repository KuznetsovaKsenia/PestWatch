from dataclasses import dataclass

from .degree_days_result import DegreeDaysResult
from .soil_temperature_estimate import SoilTemperatureEstimate
from .weather_data import WeatherData


@dataclass(frozen=True)
class RiskContext:
    weather: WeatherData
    soil_temperature_10cm_estimate: (
        SoilTemperatureEstimate | None
    ) = None
    degree_days_10c: DegreeDaysResult | None = None