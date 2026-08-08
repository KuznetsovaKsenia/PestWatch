from datetime import datetime

import pytest

from app.domain import (
    RiskFactorState,
    WeatherData,
)
from app.risk.calculators import TickRiskCalculator


def create_weather(
    temperature: float | None,
) -> WeatherData:
    return WeatherData(
        observed_at=datetime(2026, 8, 8, 12, 0),
        temperature=temperature,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )


@pytest.mark.parametrize(
    ("temperature", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.NOT_MATCHED),
        (9.9, RiskFactorState.NOT_MATCHED),
        (10.0, RiskFactorState.MATCHED),
        (10.1, RiskFactorState.MATCHED),
        (25.0, RiskFactorState.MATCHED),
    ],
)
def test_tick_temperature_rule(
    temperature,
    expected_state,
):
    calculator = TickRiskCalculator()

    factors = calculator.evaluate(
        create_weather(temperature),
    )

    assert len(factors) == 1
    assert factors[0].state == expected_state


def test_tick_returns_air_temperature_factor():
    calculator = TickRiskCalculator()

    factor = calculator.evaluate(
        create_weather(12.0),
    )[0]

    assert factor.factor == "AIR_TEMPERATURE"


def test_tick_factor_is_required():
    calculator = TickRiskCalculator()

    factor = calculator.evaluate(
        create_weather(12.0),
    )[0]

    assert factor.required is True


def test_tick_preserves_actual_temperature():
    calculator = TickRiskCalculator()

    factor = calculator.evaluate(
        create_weather(12.3),
    )[0]

    assert factor.actual_value == 12.3


def test_tick_contains_expected_threshold():
    calculator = TickRiskCalculator()

    factor = calculator.evaluate(
        create_weather(12.0),
    )[0]

    assert factor.expected == ">= 10 °C"


@pytest.mark.parametrize(
    "temperature",
    [
        None,
        5.0,
        12.0,
    ],
)
def test_tick_factor_contains_explanation(
    temperature,
):
    calculator = TickRiskCalculator()

    factor = calculator.evaluate(
        create_weather(temperature),
    )[0]

    assert factor.explanation