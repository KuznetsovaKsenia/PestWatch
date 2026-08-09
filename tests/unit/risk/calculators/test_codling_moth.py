from datetime import date, datetime

import pytest

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    RiskFactorState,
    WeatherData,
)
from app.risk.calculators import CodlingMothRiskCalculator


def create_weather(
    total: float | None,
) -> WeatherData:
    degree_days = None

    if total is not None:
        observations = (
            DailyTemperature(
                date=date(2026, 5, 1),
                mean_temperature=20.0,
            ),
        )

        degree_days = DegreeDaysResult(
            base_temperature=10.0,
            total=total,
            period_start=date(2026, 5, 1),
            period_end=date(2026, 5, 1),
            observations=observations,
            method=(
                DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
            ),
        )

    return WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=None,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
        degree_days_10c=degree_days,
    )


@pytest.mark.parametrize(
    ("total", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.NOT_MATCHED),
        (129.9, RiskFactorState.NOT_MATCHED),
        (130.0, RiskFactorState.MATCHED),
        (130.1, RiskFactorState.MATCHED),
        (500.0, RiskFactorState.MATCHED),
    ],
)
def test_codling_moth_degree_days_rule(
    total,
    expected_state,
):
    calculator = CodlingMothRiskCalculator()

    factor = calculator.evaluate(
        create_weather(total)
    )[0]

    assert factor.state == expected_state


def test_codling_moth_returns_expected_factor():
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(130.0)
    )[0]

    assert factor.factor == "DEGREE_DAYS_ABOVE_10C"


def test_codling_moth_factor_is_required():
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(130.0)
    )[0]

    assert factor.required is True


def test_codling_moth_preserves_degree_days_total():
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(137.4)
    )[0]

    assert factor.actual_value == 137.4


def test_codling_moth_missing_has_no_actual_value():
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(None)
    )[0]

    assert factor.actual_value is None


def test_codling_moth_contains_expected_threshold():
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(130.0)
    )[0]

    assert "130" in factor.expected
    assert "10" in factor.expected


@pytest.mark.parametrize(
    "total",
    [
        None,
        100.0,
        150.0,
    ],
)
def test_codling_moth_contains_explanation(total):
    factor = CodlingMothRiskCalculator().evaluate(
        create_weather(total)
    )[0]

    assert factor.explanation