from dataclasses import replace
from datetime import date, datetime, timedelta

from app.domain import (
    DailyTemperature,
    RiskFactorState,
    RiskLevel,
    RiskStatus,
    WeatherData,
)
from app.risk import RiskEngine, RiskPolicy
from app.risk.calculators import CodlingMothRiskCalculator
from app.weather import DegreeDaysCalculator


def create_observations(
    *,
    days: int,
    mean_temperature: float,
) -> tuple[DailyTemperature, ...]:
    start_date = date(2026, 5, 1)

    return tuple(
        DailyTemperature(
            date=start_date + timedelta(days=index),
            mean_temperature=mean_temperature,
        )
        for index in range(days)
    )


def create_weather() -> WeatherData:
    return WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=None,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )


def evaluate(
    observations: tuple[DailyTemperature, ...],
):
    degree_days = DegreeDaysCalculator().calculate(
        observations
    )

    weather = replace(
        create_weather(),
        degree_days_10c=degree_days,
    )

    factors = CodlingMothRiskCalculator().evaluate(
        weather
    )

    return RiskEngine(
        policy=RiskPolicy(),
    ).evaluate(
        threat_code="CODLING_MOTH",
        factors=factors,
    )


def test_codling_moth_degree_days_produce_high_risk():
    observations = create_observations(
        days=13,
        mean_temperature=20.0,
    )

    result = evaluate(observations)

    assert result.threat_code == "CODLING_MOTH"
    assert result.status == RiskStatus.CALCULATED
    assert result.risk_level == RiskLevel.HIGH

    assert len(result.factors) == 1

    factor = result.factors[0]

    assert factor.state == RiskFactorState.MATCHED
    assert factor.actual_value == 130.0


def test_codling_moth_degree_days_produce_low_risk():
    observations = create_observations(
        days=10,
        mean_temperature=20.0,
    )

    result = evaluate(observations)

    assert result.threat_code == "CODLING_MOTH"
    assert result.status == RiskStatus.CALCULATED
    assert result.risk_level == RiskLevel.LOW

    factor = result.factors[0]

    assert factor.state == RiskFactorState.NOT_MATCHED
    assert factor.actual_value == 100.0


def test_codling_moth_missing_historical_data_is_insufficient():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=None,
        ),
    )

    result = evaluate(observations)

    assert result.threat_code == "CODLING_MOTH"
    assert result.status == RiskStatus.INSUFFICIENT_DATA
    assert result.risk_level is None

    factor = result.factors[0]

    assert factor.state == RiskFactorState.MISSING
    assert factor.actual_value is None