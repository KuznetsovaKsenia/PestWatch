from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    WeatherData,
)
from app.risk.calculator import RiskCalculator


class TickRiskCalculator(RiskCalculator):
    TEMPERATURE_THRESHOLD = 10.0

    def evaluate(
        self,
        weather: WeatherData,
    ) -> tuple[RiskFactorResult, ...]:
        temperature = weather.temperature

        if temperature is None:
            state = RiskFactorState.MISSING
            explanation = (
                "Данные о температуре воздуха отсутствуют."
            )
        elif temperature >= self.TEMPERATURE_THRESHOLD:
            state = RiskFactorState.MATCHED
            explanation = (
                "Температура воздуха соответствует условиям "
                "выраженной активности иксодовых клещей."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Температура воздуха не соответствует выбранному "
                "условию выраженной активности иксодовых клещей."
            )

        return (
            RiskFactorResult(
                factor="AIR_TEMPERATURE",
                state=state,
                actual_value=temperature,
                expected=">= 10 °C",
                explanation=explanation,
                required=True,
            ),
        )