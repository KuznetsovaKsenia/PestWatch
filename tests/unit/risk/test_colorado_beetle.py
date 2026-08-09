from datetime import datetime

import pytest

from app.domain import (
    RiskFactorState,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    WeatherData,
)
from app.risk.calculators import ColoradoBeetleRiskCalculator


def create_weather(
    estimated_temperature: float | None,
) -> WeatherData:
    estimate = None

    if estimated_temperature is not None:
        estimate = SoilTemperatureEstimate(
            depth_cm=10.0,
            temperature=estimated_temperature,
            source_depths_cm=(6.0, 18.0),
            source_temperatures=(16.0, 10.0),
            method=(
                SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
            ),
        )

    return WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=None,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
        soil_temperature_10cm_estimate=estimate,
    )


@pytest.mark.parametrize(
    ("estimated_temperature", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (-5.0, RiskFactorState.NOT_MATCHED),
        (0.0, RiskFactorState.NOT_MATCHED),
        (12.9, RiskFactorState.NOT_MATCHED),
        (13.0, RiskFactorState.MATCHED),
        (13.1, RiskFactorState.MATCHED),
        (20.0, RiskFactorState.MATCHED),
    ],
)
def test_colorado_beetle_soil_temperature_rule(
    estimated_temperature,
    expected_state,
):
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(estimated_temperature)
    )[0]

    assert factor.state == expected_state


def test_colorado_beetle_returns_expected_factor():
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(14.0)
    )[0]

    assert factor.factor == "SOIL_TEMPERATURE_10CM"


def test_colorado_beetle_factor_is_required():
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(14.0)
    )[0]

    assert factor.required is True


def test_colorado_beetle_preserves_estimated_temperature():
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(14.2)
    )[0]

    assert factor.actual_value == 14.2


def test_colorado_beetle_contains_expected_threshold():
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(14.0)
    )[0]

    assert factor.expected == ">= 13 °C"


@pytest.mark.parametrize(
    "estimated_temperature",
    [
        None,
        12.0,
        14.0,
    ],
)
def test_colorado_beetle_contains_explanation(
    estimated_temperature,
):
    calculator = ColoradoBeetleRiskCalculator()

    factor = calculator.evaluate(
        create_weather(estimated_temperature)
    )[0]

    assert factor.explanation