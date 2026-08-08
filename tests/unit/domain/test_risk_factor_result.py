from app.domain import RiskFactorResult, RiskFactorState


def test_risk_factor_result_can_be_created_as_matched():
    result = RiskFactorResult(
        factor="TEMPERATURE",
        state=RiskFactorState.MATCHED,
        actual_value=18.4,
        expected=">= 10 °C",
        explanation="Температура соответствует условиям активности.",
    )

    assert result.factor == "TEMPERATURE"
    assert result.state == RiskFactorState.MATCHED
    assert result.actual_value == 18.4
    assert result.expected == ">= 10 °C"
    assert result.explanation == (
        "Температура соответствует условиям активности."
    )


def test_risk_factor_result_can_be_created_as_not_matched():
    result = RiskFactorResult(
        factor="HUMIDITY",
        state=RiskFactorState.NOT_MATCHED,
        actual_value=35.0,
        expected="60–80 %",
        explanation="Влажность не соответствует благоприятному диапазону.",
    )

    assert result.state == RiskFactorState.NOT_MATCHED
    assert result.actual_value == 35.0


def test_risk_factor_result_can_be_created_as_missing():
    result = RiskFactorResult(
        factor="SOIL_TEMPERATURE",
        state=RiskFactorState.MISSING,
        actual_value=None,
        expected=">= 10 °C",
        explanation="Данные о температуре почвы отсутствуют.",
    )

    assert result.state == RiskFactorState.MISSING
    assert result.actual_value is None


def test_missing_state_is_different_from_not_matched():
    missing = RiskFactorResult(
        factor="HUMIDITY",
        state=RiskFactorState.MISSING,
        actual_value=None,
        expected="60–80 %",
        explanation="Данные отсутствуют.",
    )

    not_matched = RiskFactorResult(
        factor="HUMIDITY",
        state=RiskFactorState.NOT_MATCHED,
        actual_value=35.0,
        expected="60–80 %",
        explanation="Условие не выполнено.",
    )

    assert missing.state != not_matched.state