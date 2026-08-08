from abc import ABC, abstractmethod

from app.domain import RiskFactorResult, WeatherData


class RiskCalculator(ABC):
    @abstractmethod
    def evaluate(
        self,
        weather: WeatherData,
    ) -> tuple[RiskFactorResult, ...]:
        ...