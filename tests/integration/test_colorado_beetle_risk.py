from datetime import datetime

import pytest

from app.domain import (
    RiskContext,
    RiskFactorState,
    RiskLevel,
    RiskStatus,
    WeatherData,
)
from app.risk import RiskEngine, RiskPolicy
from app.risk.calculators import ColoradoBeetleRiskCalculator
from app.weather import SoilTemperatureEstimator


def create_weather(
    *,
    temperature_6cm: float | None,
    temperature_18cm: float | None,
) -> WeatherData:
    return WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=None,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
        soil_temperature_6cm=temperature_6cm,
        soil_temperature_18cm=temperature_18cm,
    )


def evaluate(
    *,
    temperature_6cm: float | None,
    temperature_18cm: float | None,
):
    weather = create_weather(
        temperature_6cm=temperature_6cm,
        temperature_18cm=temperature_18cm,
    )

    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=weather.soil_temperature_6cm,
        temperature_18cm=weather.soil_temperature_18cm,
    )

    context = RiskContext(
        weather=weather,
        soil_temperature_10cm_estimate=estimate,
    )

    calculator = ColoradoBeetleRiskCalculator()

    factors = calculator.evaluate(
        context
    )

    engine = RiskEngine(
        policy=RiskPolicy(),
    )

    return engine.evaluate(
        threat_code="COLORADO_BEETLE",
        factors=factors,
    )


@pytest.mark.parametrize(
    (
        "temperature_6cm",
        "temperature_18cm",
        "expected_estimated_temperature",
        "expected_factor_state",
        "expected_status",
        "expected_level",
    ),
    [
        (
            16.0,
            10.0,
            14.0,
            RiskFactorState.MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.HIGH,
        ),
        (
            12.0,
            9.0,
            11.0,
            RiskFactorState.MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.HIGH,
        ),
        (
            None,
            14.0,
            None,
            RiskFactorState.MISSING,
            RiskStatus.INSUFFICIENT_DATA,
            None,
        ),
    ],
)
def test_colorado_beetle_estimation_to_risk_engine(
    temperature_6cm,
    temperature_18cm,
    expected_estimated_temperature,
    expected_factor_state,
    expected_status,
    expected_level,
):
    result = evaluate(
        temperature_6cm=temperature_6cm,
        temperature_18cm=temperature_18cm,
    )

    factor = result.factors[0]

    assert result.threat_code == "COLORADO_BEETLE"
    assert factor.state == expected_factor_state
    assert result.status == expected_status
    assert result.risk_level == expected_level

    if expected_estimated_temperature is None:
        assert factor.actual_value is None
    else:
        assert factor.actual_value == pytest.approx(
            expected_estimated_temperature
        )