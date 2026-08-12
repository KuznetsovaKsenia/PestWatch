from datetime import datetime

import pytest

from app.domain import (
    RiskContext,
    RiskFactorState,
    WeatherData,
)
from app.risk.calculators import TickRiskCalculator


def create_context(
    *,
    temperature: float | None,
    saturation_deficit: float | None,
) -> RiskContext:
    weather = WeatherData(
        observed_at=datetime(2026, 8, 8, 12, 0),
        temperature=temperature,
        humidity=80.0,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )

    return RiskContext(
        weather=weather,
        saturation_deficit_mm_hg=(
            saturation_deficit
        ),
    )


@pytest.mark.parametrize(
    ("temperature", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.NOT_MATCHED),
        (9.9, RiskFactorState.NOT_MATCHED),
        (10.0, RiskFactorState.MATCHED),
        (18.0, RiskFactorState.MATCHED),
    ],
)
def test_tick_temperature_rule(
    temperature,
    expected_state,
):
    factors = TickRiskCalculator().evaluate(
        create_context(
            temperature=temperature,
            saturation_deficit=1.0,
        )
    )

    assert factors[0].state == expected_state


@pytest.mark.parametrize(
    ("saturation_deficit", "expected_state"),
    [
        (None, RiskFactorState.MISSING),
        (0.0, RiskFactorState.MATCHED),
        (4.999, RiskFactorState.MATCHED),
        (5.0, RiskFactorState.NOT_MATCHED),
        (8.0, RiskFactorState.NOT_MATCHED),
    ],
)
def test_tick_saturation_deficit_rule(
    saturation_deficit,
    expected_state,
):
    factors = TickRiskCalculator().evaluate(
        create_context(
            temperature=18.0,
            saturation_deficit=saturation_deficit,
        )
    )

    assert factors[1].state == expected_state


def test_tick_returns_two_required_factors():
    factors = TickRiskCalculator().evaluate(
        create_context(
            temperature=18.0,
            saturation_deficit=1.5,
        )
    )

    assert tuple(
        factor.factor for factor in factors
    ) == (
        "AIR_TEMPERATURE",
        "SATURATION_DEFICIT",
    )

    assert all(
        factor.required
        for factor in factors
    )


def test_tick_preserves_engineering_actual_values():
    factors = TickRiskCalculator().evaluate(
        create_context(
            temperature=18.4,
            saturation_deficit=1.25,
        )
    )

    assert factors[0].actual_value == 18.4
    assert factors[1].actual_value == 1.25


def test_tick_contains_expected_thresholds():
    factors = TickRiskCalculator().evaluate(
        create_context(
            temperature=18.0,
            saturation_deficit=1.5,
        )
    )

    assert factors[0].expected == ">= 10 °C"
    assert factors[1].expected == "< 5 mmHg"
