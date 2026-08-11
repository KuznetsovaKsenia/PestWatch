from app.domain import (
    RiskContext,
    RiskFactorResult,
    RiskFactorState,
)
from app.risk.calculator import RiskCalculator


class TickRiskCalculator(RiskCalculator):
    TEMPERATURE_THRESHOLD = 10.0
    SATURATION_DEFICIT_THRESHOLD = 5.0

    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        return (
            self._evaluate_temperature(
                context.weather.temperature
            ),
            self._evaluate_saturation_deficit(
                context.saturation_deficit_mm_hg
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
        elif temperature >= self.TEMPERATURE_THRESHOLD:
            state = RiskFactorState.MATCHED
            explanation = (
                "Температура воздуха позволяет иксодовым клещам "
                "сохранять активность."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Температура воздуха ниже выбранного порога "
                "потенциальной активности иксодовых клещей."
            )

        return RiskFactorResult(
            factor="AIR_TEMPERATURE",
            state=state,
            actual_value=temperature,
            expected=">= 10 °C",
            explanation=explanation,
            required=True,
        )

    def _evaluate_saturation_deficit(
        self,
        saturation_deficit: float | None,
    ) -> RiskFactorResult:
        if saturation_deficit is None:
            state = RiskFactorState.MISSING
            explanation = (
                "Недостаточно данных температуры и влажности "
                "для оценки высушивающего действия воздуха."
            )
        elif (
            saturation_deficit
            < self.SATURATION_DEFICIT_THRESHOLD
        ):
            state = RiskFactorState.MATCHED
            explanation = (
                "Температура и влажность соответствуют условиям "
                "с низким риском высыхания для активных клещей."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            explanation = (
                "Воздух оказывает более выраженное высушивающее "
                "действие, ограничивающее длительную активность клещей."
            )

        return RiskFactorResult(
            factor="SATURATION_DEFICIT",
            state=state,
            actual_value=saturation_deficit,
            expected="< 5 mmHg",
            explanation=explanation,
            required=True,
        )
