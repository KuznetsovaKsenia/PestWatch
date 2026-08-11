from datetime import datetime

import pytest

from app.domain import (
    RiskContext,
    RiskFactorState,
    WeatherData,
)
from app.risk.calculators import CabbageAphidRiskCalculator


def create_context(
    *,
    temperature: float | None,
    humidity: float | None = 65.0,
) -> RiskContext:
    weather = WeatherData(
        observed_at=datetime(2026, 8, 8, 12, 0),
        temperature=temperature,
        humidity=humidity,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )

    return RiskContext(
        weather=weather,
    )


@pytest.mark.parametrize(
    ("temperature", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.NOT_MATCHED),
        (14.9, RiskFactorState.NOT_MATCHED),
        (15.0, RiskFactorState.MATCHED),
        (18.0, RiskFactorState.MATCHED),
        (20.0, RiskFactorState.MATCHED),
        (25.0, RiskFactorState.MATCHED),
        (25.1, RiskFactorState.NOT_MATCHED),
        (30.0, RiskFactorState.NOT_MATCHED),
    ],
)
def test_temperature_rule(
    temperature,
    expected_state,
):
    factors = CabbageAphidRiskCalculator().evaluate(
        create_context(
            temperature=temperature,
        )
    )

    assert factors[0].state == expected_state


def test_calculator_returns_only_temperature_factor():
    factors = CabbageAphidRiskCalculator().evaluate(
        create_context(
            temperature=18.0,
            humidity=91.0,
        )
    )

    assert len(factors) == 1
    assert (
        factors[0].factor
        == "AIR_TEMPERATURE"
    )


def test_humidity_does_not_change_temperature_factor():
    calculator = CabbageAphidRiskCalculator()

    dry = calculator.evaluate(
        create_context(
            temperature=18.0,
            humidity=30.0,
        )
    )[0]

    humid = calculator.evaluate(
        create_context(
            temperature=18.0,
            humidity=91.0,
        )
    )[0]

    assert dry.state == RiskFactorState.MATCHED
    assert humid.state == RiskFactorState.MATCHED


def test_temperature_factor_preserves_actual_value():
    factor = CabbageAphidRiskCalculator().evaluate(
        create_context(
            temperature=18.4,
        )
    )[0]

    assert factor.actual_value == 18.4


def test_temperature_factor_contains_expected_range():
    factor = CabbageAphidRiskCalculator().evaluate(
        create_context(
            temperature=18.0,
        )
    )[0]

    assert factor.expected == "15–25 °C"
