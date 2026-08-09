from dataclasses import dataclass
from datetime import date

from app.domain.daily_temperature import DailyTemperature
from app.domain.degree_days_calculation_method import (
    DegreeDaysCalculationMethod,
)


@dataclass(frozen=True)
class DegreeDaysResult:
    base_temperature: float
    total: float
    period_start: date
    period_end: date
    observations: tuple[DailyTemperature, ...]
    method: DegreeDaysCalculationMethod