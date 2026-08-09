from datetime import datetime

import pytest

from app.domain import (
    RiskFactorState,
    WeatherData,
    RiskContext,
)
from app.risk.calculators import CabbageAphidRiskCalculator


def create_context(
    *,
    temperature: float | None,
    humidity: float | None,
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
        (24.9, RiskFactorState.NOT_MATCHED),
        (25.0, RiskFactorState.MATCHED),
        (25.5, RiskFactorState.MATCHED),
        (26.0, RiskFactorState.MATCHED),
        (26.1, RiskFactorState.NOT_MATCHED),
    ],
)
def test_temperature_rule(
    temperature,
    expected_state,
):
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=temperature,
            humidity=65.0,
        )
    )

    assert factors[0].state == expected_state


@pytest.mark.parametrize(
    ("humidity", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.NOT_MATCHED),
        (59.9, RiskFactorState.NOT_MATCHED),
        (60.0, RiskFactorState.MATCHED),
        (65.0, RiskFactorState.MATCHED),
        (70.0, RiskFactorState.MATCHED),
        (70.1, RiskFactorState.NOT_MATCHED),
        (100.0, RiskFactorState.NOT_MATCHED),
    ],
)
def test_humidity_rule(
    humidity,
    expected_state,
):
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=humidity,
        )
    )

    assert factors[1].state == expected_state


def test_calculator_returns_factors_in_stable_order():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert tuple(
        factor.factor for factor in factors
    ) == (
        "AIR_TEMPERATURE",
        "RELATIVE_HUMIDITY",
    )


def test_both_factors_are_required():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert all(factor.required for factor in factors)


def test_temperature_factor_preserves_actual_value():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert factors[0].actual_value == 25.5


def test_humidity_factor_preserves_actual_value():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert factors[1].actual_value == 65.0


def test_temperature_factor_contains_expected_range():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert factors[0].expected == "25–26 °C"


def test_humidity_factor_contains_expected_range():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert factors[1].expected == "60–70 %"


def test_factors_contain_explanations():
    calculator = CabbageAphidRiskCalculator()

    factors = calculator.evaluate(
        create_context(
            temperature=25.5,
            humidity=65.0,
        )
    )

    assert all(
        factor.explanation
        for factor in factors
    )