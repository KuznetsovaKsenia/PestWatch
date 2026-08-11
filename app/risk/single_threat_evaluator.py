from app.domain import (
    DailyTemperature,
    RiskContext,
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
        degree_days_season_started: bool | None = None,
    ) -> RiskResult:
        result, _ = self.evaluate_with_context(
            threat_code,
            weather=weather,
            historical_temperatures=(
                historical_temperatures
            ),
            degree_days_season_started=(
                degree_days_season_started
            ),
        )

        return result

    def evaluate_with_context(
        self,
        threat_code: str,
        *,
        weather: WeatherData | None = None,
        historical_temperatures: (
            tuple[DailyTemperature, ...] | None
        ) = None,
        degree_days_season_started: bool | None = None,
    ) -> tuple[
        RiskResult,
        RiskContext,
    ]:
        context = self._context_preparer.prepare(
            threat_code,
            weather=weather,
            historical_temperatures=(
                historical_temperatures
            ),
            degree_days_season_started=(
                degree_days_season_started
            ),
        )

        calculator = self._calculator_registry.get(
            threat_code
        )

        factors = calculator.evaluate(
            context
        )

        result = self._engine.evaluate(
            threat_code=threat_code,
            factors=factors,
        )

        return result, context
