from dataclasses import dataclass
from datetime import date

from app.domain import DailyTemperature, Location, WeatherData


@dataclass(frozen=True)
class DemoScenario:
    scenario_id: str
    location: Location
    assessment_date: date
    current_weather: WeatherData
    historical_temperatures: tuple[DailyTemperature, ...]
