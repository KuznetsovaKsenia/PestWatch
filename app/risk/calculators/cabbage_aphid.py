from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskContext,
)
from app.risk.calculator import RiskCalculator


class CabbageAphidRiskCalculator(RiskCalculator):
    TEMPERATURE_MIN = 25.0
    TEMPERATURE_MAX = 26.0

    HUMIDITY_MIN = 60.0
    HUMIDITY_MAX = 70.0

    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        return (
            self._evaluate_temperature(context.weather.temperature),
            self._evaluate_humidity(context.weather.humidity),
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
                "Температура воздуха соответствует оптимальным "
                "условиям активности капустной тли."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Температура воздуха не соответствует выбранному "
                "оптимальному диапазону активности капустной тли."
            )

        return RiskFactorResult(
            factor="AIR_TEMPERATURE",
            state=state,
            actual_value=temperature,
            expected="25–26 °C",
            explanation=explanation,
            required=True,
        )

    def _evaluate_humidity(
        self,
        humidity: float | None,
    ) -> RiskFactorResult:
        if humidity is None:
            state = RiskFactorState.MISSING
            explanation = (
                "Данные об относительной влажности отсутствуют."
            )
        elif (
            self.HUMIDITY_MIN
            <= humidity
            <= self.HUMIDITY_MAX
        ):
            state = RiskFactorState.MATCHED
            explanation = (
                "Относительная влажность соответствует оптимальным "
                "условиям активности капустной тли."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Относительная влажность не соответствует выбранному "
                "оптимальному диапазону активности капустной тли."
            )

        return RiskFactorResult(
            factor="RELATIVE_HUMIDITY",
            state=state,
            actual_value=humidity,
            expected="60–70 %",
            explanation=explanation,
            required=True,
        )