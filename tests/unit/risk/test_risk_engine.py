from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskStatus,
)
from app.risk import RiskEngine, RiskPolicy


def create_factor(
    state: RiskFactorState,
    *,
    required: bool = True,
) -> RiskFactorResult:
    return RiskFactorResult(
        factor="TEST_FACTOR",
        state=state,
        actual_value=None,
        expected=None,
        explanation="Test factor.",
        required=required,
    )


def create_engine() -> RiskEngine:
    return RiskEngine(
        policy=RiskPolicy(),
    )


def test_engine_preserves_threat_code():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(
            create_factor(RiskFactorState.MATCHED),
        ),
    )

    assert result.threat_code == "TICK"


def test_engine_preserves_factors():
    engine = create_engine()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
    )

    result = engine.evaluate(
        threat_code="TICK",
        factors=factors,
    )

    assert result.factors == factors


def test_engine_returns_calculated_result():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(
            create_factor(RiskFactorState.MATCHED),
            create_factor(RiskFactorState.MATCHED),
        ),
    )

    assert result.status == RiskStatus.CALCULATED
    assert result.risk_level == RiskLevel.HIGH
    assert result.explanation == (
        "Оценка выполнена по всем доступным факторам."
    )


def test_engine_returns_limited_result():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(
            create_factor(RiskFactorState.MATCHED),
            create_factor(
                RiskFactorState.MISSING,
                required=False,
            ),
        ),
    )

    assert result.status == RiskStatus.LIMITED
    assert result.risk_level == RiskLevel.HIGH
    assert result.explanation == (
        "Оценка выполнена по обязательным факторам, "
        "часть дополнительных данных отсутствует."
    )


def test_engine_returns_insufficient_data_for_required_missing():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(
            create_factor(RiskFactorState.MISSING),
        ),
    )

    assert result.status == RiskStatus.INSUFFICIENT_DATA
    assert result.risk_level is None
    assert result.explanation == (
        "Недостаточно обязательных данных для оценки."
    )


def test_engine_returns_insufficient_data_for_empty_factors():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(),
    )

    assert result.status == RiskStatus.INSUFFICIENT_DATA
    assert result.risk_level is None


def test_engine_uses_policy_risk_level():
    engine = create_engine()

    result = engine.evaluate(
        threat_code="TICK",
        factors=(
            create_factor(RiskFactorState.MATCHED),
            create_factor(RiskFactorState.NOT_MATCHED),
        ),
    )

    assert result.status == RiskStatus.CALCULATED
    assert result.risk_level == RiskLevel.ELEVATED