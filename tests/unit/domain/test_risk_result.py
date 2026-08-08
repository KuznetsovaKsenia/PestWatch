import pytest

from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskResult,
    RiskStatus,
)


def create_temperature_factor():
    return RiskFactorResult(
        factor="TEMPERATURE",
        state=RiskFactorState.MATCHED,
        actual_value=18.4,
        expected=">= 10 °C",
        explanation="Температура соответствует условиям активности.",
    )


def test_calculated_result_requires_risk_level():
    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.ELEVATED,
        factors=(create_temperature_factor(),),
        explanation="Условия соответствуют периоду активности.",
    )

    assert result.threat_code == "TICK"
    assert result.status == RiskStatus.CALCULATED
    assert result.risk_level == RiskLevel.ELEVATED
    assert len(result.factors) == 1


def test_calculated_result_without_risk_level_is_rejected():
    with pytest.raises(
        ValueError,
        match="RiskLevel is required when status is CALCULATED",
    ):
        RiskResult(
            threat_code="TICK",
            status=RiskStatus.CALCULATED,
            risk_level=None,
            factors=(),
            explanation="",
        )


def test_limited_result_can_have_risk_level():
    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.LIMITED,
        risk_level=RiskLevel.MODERATE,
        factors=(create_temperature_factor(),),
        explanation="Оценка выполнена с ограниченным набором данных.",
    )

    assert result.status == RiskStatus.LIMITED
    assert result.risk_level == RiskLevel.MODERATE


def test_insufficient_data_result_can_have_no_risk_level():
    result = RiskResult(
        threat_code="COLORADO_BEETLE",
        status=RiskStatus.INSUFFICIENT_DATA,
        risk_level=None,
        factors=(),
        explanation="Недостаточно данных для оценки.",
    )

    assert result.status == RiskStatus.INSUFFICIENT_DATA
    assert result.risk_level is None


def test_error_result_can_have_no_risk_level():
    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.ERROR,
        risk_level=None,
        factors=(),
        explanation="Не удалось выполнить оценку.",
    )

    assert result.status == RiskStatus.ERROR
    assert result.risk_level is None


def test_risk_result_can_contain_multiple_factors():
    temperature = create_temperature_factor()

    season = RiskFactorResult(
        factor="SEASON",
        state=RiskFactorState.MATCHED,
        actual_value="AUGUST",
        expected="APRIL–OCTOBER",
        explanation="Дата входит в сезон активности.",
    )

    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.ELEVATED,
        factors=(temperature, season),
        explanation="Несколько факторов соответствуют условиям активности.",
    )

    assert len(result.factors) == 2
    assert result.factors[0] == temperature
    assert result.factors[1] == season


def test_risk_result_factors_are_immutable():
    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.ELEVATED,
        factors=(create_temperature_factor(),),
        explanation="Условия соответствуют периоду активности.",
    )

    assert isinstance(result.factors, tuple)

    with pytest.raises(TypeError):
        result.factors[0] = create_temperature_factor()