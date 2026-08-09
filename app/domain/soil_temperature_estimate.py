from dataclasses import dataclass

from app.domain.soil_temperature_estimate_method import (
    SoilTemperatureEstimateMethod,
)


@dataclass(frozen=True)
class SoilTemperatureEstimate:
    depth_cm: float
    temperature: float
    source_depths_cm: tuple[float, float]
    source_temperatures: tuple[float, float]
    method: SoilTemperatureEstimateMethod