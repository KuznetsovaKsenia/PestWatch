from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    RiskContext,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    WeatherData,
)


def create_weather():
    return WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=18.4,
        humidity=67.0,
        precipitation=0.0,
        wind_speed=3.2,
        soil_temperature=16.1,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )


def create_soil_temperature_estimate():
    return SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(6.0, 18.0),
        source_temperatures=(16.0, 10.0),
        method=(
            SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
        ),
    )


def create_degree_days_result():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
    )

    return DegreeDaysResult(
        base_temperature=10.0,
        total=10.0,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 1),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
        ),
    )


def test_context_preserves_weather():
    weather = create_weather()

    context = RiskContext(
        weather=weather,
    )

    assert context.weather is weather

def test_context_allows_missing_weather():
    context = RiskContext()

    assert context.weather is None

def test_context_can_store_degree_days_without_weather():
    degree_days = create_degree_days_result()

    context = RiskContext(
        degree_days_10c=degree_days,
    )

    assert context.weather is None
    assert context.degree_days_10c is degree_days


def test_context_defaults_derived_inputs_to_none():
    context = RiskContext(
        weather=create_weather(),
    )

    assert context.soil_temperature_10cm_estimate is None
    assert context.degree_days_10c is None


def test_context_preserves_soil_temperature_estimate():
    estimate = create_soil_temperature_estimate()

    context = RiskContext(
        weather=create_weather(),
        soil_temperature_10cm_estimate=estimate,
    )

    assert context.soil_temperature_10cm_estimate is estimate


def test_context_preserves_degree_days_result():
    degree_days = create_degree_days_result()

    context = RiskContext(
        weather=create_weather(),
        degree_days_10c=degree_days,
    )

    assert context.degree_days_10c is degree_days


def test_context_preserves_all_inputs():
    weather = create_weather()
    estimate = create_soil_temperature_estimate()
    degree_days = create_degree_days_result()

    context = RiskContext(
        weather=weather,
        soil_temperature_10cm_estimate=estimate,
        degree_days_10c=degree_days,
    )

    assert context.weather is weather
    assert context.soil_temperature_10cm_estimate is estimate
    assert context.degree_days_10c is degree_days


@pytest.mark.parametrize(
    ("field_name", "new_value"),
    [
        ("weather", None),
        ("soil_temperature_10cm_estimate", None),
        ("degree_days_10c", None),
    ],
)
def test_context_is_immutable(
    field_name,
    new_value,
):
    context = RiskContext(
        weather=create_weather(),
        soil_temperature_10cm_estimate=(
            create_soil_temperature_estimate()
        ),
        degree_days_10c=create_degree_days_result(),
    )

    with pytest.raises(FrozenInstanceError):
        setattr(
            context,
            field_name,
            new_value,
        )

def test_context_preserves_saturation_deficit():
    context = RiskContext(
        weather=create_weather(),
        saturation_deficit_mm_hg=1.25,
    )

    assert (
        context.saturation_deficit_mm_hg
        == pytest.approx(1.25)
    )
