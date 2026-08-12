from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskContext,
)
from app.risk.calculator import RiskCalculator


class CodlingMothRiskCalculator(RiskCalculator):
    DEGREE_DAYS_THRESHOLD = 130.0

    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        degree_days = context.degree_days_10c

        if context.degree_days_season_started is False:
            state = RiskFactorState.NOT_MATCHED
            actual_value = 0.0
            explanation = (
                "Первые три последовательных дня со средней суточной "
                "температурой выше 10 °C ещё не зафиксированы; "
                "сезонное накопление эффективных температур не началось."
            )
        elif degree_days is None:
            state = RiskFactorState.MISSING
            actual_value = None
            explanation = (
                "Недостаточно исторических температур для расчёта "
                "сезонного показателя яблонной плодожорки."
            )
        elif degree_days.total >= self.DEGREE_DAYS_THRESHOLD:
            state = RiskFactorState.MATCHED
            actual_value = degree_days.total
            explanation = (
                "Накопленная сумма эффективных температур достигла "
                "рабочего порога PestWatch, указывающего на период "
                "возможной сезонной активности яблонной плодожорки."
            )
        else:
            state = RiskFactorState.NOT_MATCHED
            actual_value = degree_days.total
            explanation = (
                "Накопленная сумма эффективных температур пока ниже "
                "рабочего порога PestWatch для периода возможной "
                "сезонной активности яблонной плодожорки."
            )

        return (
            RiskFactorResult(
                factor="DEGREE_DAYS_ABOVE_10C",
                state=state,
                actual_value=actual_value,
                expected=(
                    ">= 130 °C СЭТ при базовой "
                    "температуре 10 °C"
                ),
                explanation=explanation,
                required=True,
            ),
        )
