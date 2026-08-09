from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskContext,
)
from app.risk.calculator import RiskCalculator


class ColoradoBeetleRiskCalculator(RiskCalculator):
    SOIL_TEMPERATURE_THRESHOLD = 13.0

    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        estimate = context.soil_temperature_10cm_estimate

        if estimate is None:
            state = RiskFactorState.MISSING
            actual_value = None
            explanation = (
                "Недостаточно данных для оценки температуры почвы "
                "на глубине около 10 см."
            )
        elif estimate.temperature >= self.SOIL_TEMPERATURE_THRESHOLD:
            state = RiskFactorState.MATCHED
            actual_value = estimate.temperature
            explanation = (
                "Температура почвы на глубине около 10 см "
                "соответствует условиям активного выхода "
                "колорадского жука."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            actual_value = estimate.temperature
            explanation = (
                "Температура почвы на глубине около 10 см "
                "ниже уровня, связанного с активным выходом "
                "колорадского жука."
            )

        return (
            RiskFactorResult(
                factor="SOIL_TEMPERATURE_10CM",
                state=state,
                actual_value=actual_value,
                expected=">= 13 °C",
                explanation=explanation,
                required=True,
            ),
        )