from app.domain import RiskFactorResult, RiskFactorState
from app.risk import RiskEvaluation


def test_risk_evaluation_can_be_created():
    factor = RiskFactorResult(
        factor="TEMPERATURE",
        state=RiskFactorState.MATCHED,
        actual_value=18.4,
        expected=">= 10 °C",
        explanation="Температура соответствует условию.",
    )

    evaluation = RiskEvaluation(
        threat_code="TICK",
        factors=(factor,),
    )

    assert evaluation.threat_code == "TICK"
    assert evaluation.factors == (factor,)


def test_risk_evaluation_can_have_empty_factors():
    evaluation = RiskEvaluation(
        threat_code="TICK",
        factors=(),
    )

    assert evaluation.factors == ()