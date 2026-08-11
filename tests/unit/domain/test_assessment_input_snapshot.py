from datetime import date, datetime

from app.domain import (
    AssessmentInputSnapshot,
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    WeatherData,
)


def create_weather():
    return WeatherData(
        observed_at=datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        temperature=25.5,
        humidity=65.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )


def create_soil_estimate():
    return SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(
            6.0,
            18.0,
        ),
        source_temperatures=(
            16.0,
            10.0,
        ),
        method=(
            SoilTemperatureEstimateMethod
            .LINEAR_INTERPOLATION
        ),
    )


def create_observations():
    return (
        DailyTemperature(
            date=date(
                2026,
                5,
                1,
            ),
            mean_temperature=20.0,
        ),
        DailyTemperature(
            date=date(
                2026,
                5,
                2,
            ),
            mean_temperature=21.0,
        ),
    )


def create_degree_days():
    observations = create_observations()

    return DegreeDaysResult(
        base_temperature=10.0,
        total=21.0,
        period_start=date(
            2026,
            5,
            1,
        ),
        period_end=date(
            2026,
            5,
            2,
        ),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod
            .DAILY_MEAN_ABOVE_BASE
        ),
    )


def test_snapshot_can_be_empty():
    snapshot = AssessmentInputSnapshot()

    assert snapshot.current_weather is None
    assert (
        snapshot.soil_temperature_10cm_estimate
        is None
    )
    assert snapshot.degree_days_10c is None
    assert snapshot.historical_observations is None


def test_snapshot_preserves_current_weather():
    weather = create_weather()

    snapshot = AssessmentInputSnapshot(
        current_weather=weather,
    )

    assert snapshot.current_weather is weather


def test_snapshot_preserves_soil_temperature_estimate():
    estimate = create_soil_estimate()

    snapshot = AssessmentInputSnapshot(
        soil_temperature_10cm_estimate=estimate,
    )

    assert (
        snapshot.soil_temperature_10cm_estimate
        is estimate
    )


def test_snapshot_preserves_degree_days_and_observations():
    degree_days = create_degree_days()
    observations = create_observations()

    snapshot = AssessmentInputSnapshot(
        degree_days_10c=degree_days,
        historical_observations=observations,
    )

    assert snapshot.degree_days_10c is degree_days
    assert (
        snapshot.historical_observations
        is observations
    )