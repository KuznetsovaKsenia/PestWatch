from app.domain import (
    DailyTemperature,
    RiskResult,
    WeatherData,
)
from app.risk.calculator_registry import (
    RiskCalculatorRegistry,
)
from app.risk.context_preparer import (
    RiskContextPreparer,
)
from app.risk.engine import RiskEngine


class SingleThreatRiskEvaluator:
    def __init__(
        self,
        context_preparer: RiskContextPreparer,
        calculator_registry: RiskCalculatorRegistry,
        engine: RiskEngine,
    ):
        self._context_preparer = context_preparer
        self._calculator_registry = calculator_registry
        self._engine = engine

    def evaluate(
        self,
        threat_code: str,
        *,
        weather: WeatherData | None = None,
        historical_temperatures: (
            tuple[DailyTemperature, ...] | None
        ) = None,
    ) -> RiskResult:
        context = self._context_preparer.prepare(
            threat_code,
            weather=weather,
            historical_temperatures=(
                historical_temperatures
            ),
        )

        calculator = self._calculator_registry.get(
            threat_code
        )

        factors = calculator.evaluate(
            context
        )

        return self._engine.evaluate(
            threat_code=threat_code,
            factors=factors,
        )