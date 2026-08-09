from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyTemperature:
    date: date
    mean_temperature: float | None