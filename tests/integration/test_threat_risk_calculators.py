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
from app.risk.calculators import (
    CabbageAphidRiskCalculator,
    TickRiskCalculator,
)


def create_weather(
    *,
    temperature: float | None,
    humidity: float | None = None,
) -> WeatherData:
    return WeatherData(
        observed_at=datetime(2026, 8, 8, 12, 0),
        temperature=temperature,
        humidity=humidity,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )


def evaluate(
    threat_code: str,
    calculator,
    weather: WeatherData,
    *,
    saturation_deficit: float | None = None,
):
    context = RiskContext(
        weather=weather,
        saturation_deficit_mm_hg=saturation_deficit,
    )

    factors = calculator.evaluate(
        context,
    )

    engine = RiskEngine(
        policy=RiskPolicy(),
    )

    return engine.evaluate(
        threat_code=threat_code,
        factors=factors,
    )


@pytest.mark.parametrize(
    (
        "temperature",
        "saturation_deficit",
        "expected_states",
        "expected_status",
        "expected_level",
    ),
    [
        (
            18.0,
            1.5,
            (
                RiskFactorState.MATCHED,
                RiskFactorState.MATCHED,
            ),
            RiskStatus.CALCULATED,
            RiskLevel.HIGH,
        ),
        (
            18.0,
            8.0,
            (
                RiskFactorState.MATCHED,
                RiskFactorState.NOT_MATCHED,
            ),
            RiskStatus.CALCULATED,
            RiskLevel.ELEVATED,
        ),
        (
            5.0,
            8.0,
            (
                RiskFactorState.NOT_MATCHED,
                RiskFactorState.NOT_MATCHED,
            ),
            RiskStatus.CALCULATED,
            RiskLevel.LOW,
        ),
        (
            18.0,
            None,
            (
                RiskFactorState.MATCHED,
                RiskFactorState.MISSING,
            ),
            RiskStatus.INSUFFICIENT_DATA,
            None,
        ),
    ],
)
def test_tick_calculator_to_risk_engine(
    temperature,
    saturation_deficit,
    expected_states,
    expected_status,
    expected_level,
):
    result = evaluate(
        threat_code="TICK",
        calculator=TickRiskCalculator(),
        weather=create_weather(
            temperature=temperature,
            humidity=91.0,
        ),
        saturation_deficit=saturation_deficit,
    )

    assert result.threat_code == "TICK"

    assert tuple(
        factor.state
        for factor in result.factors
    ) == expected_states

    assert result.status == expected_status
    assert result.risk_level == expected_level


@pytest.mark.parametrize(
    (
        "temperature",
        "humidity",
        "expected_state",
        "expected_status",
        "expected_level",
    ),
    [
        (
            18.0,
            91.0,
            RiskFactorState.MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.HIGH,
        ),
        (
            14.9,
            91.0,
            RiskFactorState.NOT_MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.LOW,
        ),
        (
            25.0,
            30.0,
            RiskFactorState.MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.HIGH,
        ),
        (
            25.1,
            65.0,
            RiskFactorState.NOT_MATCHED,
            RiskStatus.CALCULATED,
            RiskLevel.LOW,
        ),
        (
            None,
            65.0,
            RiskFactorState.MISSING,
            RiskStatus.INSUFFICIENT_DATA,
            None,
        ),
    ],
)
def test_cabbage_aphid_calculator_to_risk_engine(
    temperature,
    humidity,
    expected_state,
    expected_status,
    expected_level,
):
    result = evaluate(
        threat_code="CABBAGE_APHID",
        calculator=CabbageAphidRiskCalculator(),
        weather=create_weather(
            temperature=temperature,
            humidity=humidity,
        ),
    )

    assert result.threat_code == "CABBAGE_APHID"
    assert len(result.factors) == 1
    assert result.factors[0].state == expected_state
    assert result.status == expected_status
    assert result.risk_level == expected_level
