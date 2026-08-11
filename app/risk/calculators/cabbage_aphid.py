from app.domain import (
    RiskContext,
    RiskFactorResult,
    RiskFactorState,
)
from app.risk.calculator import RiskCalculator


class CabbageAphidRiskCalculator(RiskCalculator):
    TEMPERATURE_MIN = 15.0
    TEMPERATURE_MAX = 25.0

    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        return (
            self._evaluate_temperature(
                context.weather.temperature
            ),
        )

    def _evaluate_temperature(
        self,
        temperature: float | None,
    ) -> RiskFactorResult:
        if temperature is None:
            state = RiskFactorState.MISSING
            explanation = (
                "Данные о температуре воздуха отсутствуют."
            )
        elif (
            self.TEMPERATURE_MIN
            <= temperature
            <= self.TEMPERATURE_MAX
        ):
            state = RiskFactorState.MATCHED
            explanation = (
                "Температура воздуха находится в диапазоне, "
                "благоприятном для развития капустной тли."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Температура воздуха находится вне выбранного "
                "благоприятного диапазона развития капустной тли."
            )

        return RiskFactorResult(
            factor="AIR_TEMPERATURE",
            state=state,
            actual_value=temperature,
            expected="15–25 °C",
            explanation=explanation,
            required=True,
        )
