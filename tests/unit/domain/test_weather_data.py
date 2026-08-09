from datetime import date, datetime

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    WeatherData,
)

from app.domain import WeatherData
from app.domain import (
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    WeatherData,
)

def test_weather_data_degree_days_is_none_by_default():
    weather = WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
    )

    assert weather.degree_days_10c is None

def test_weather_data_can_be_created_with_all_values():
    observed_at = datetime(2026, 8, 8, 15, 0)

    weather = WeatherData(
        observed_at=observed_at,
        temperature=18.4,
        humidity=67.0,
        precipitation=1.2,
        wind_speed=3.2,
        soil_temperature=15.1,
    )

    assert weather.observed_at == observed_at
    assert weather.temperature == 18.4
    assert weather.humidity == 67.0
    assert weather.precipitation == 1.2
    assert weather.wind_speed == 3.2
    assert weather.soil_temperature == 15.1


def test_weather_data_allows_missing_values():
    weather = WeatherData(
        observed_at=datetime(2026, 8, 8, 15, 0),
        temperature=None,
        humidity=None,
        precipitation=None,
        wind_speed=None,
        soil_temperature=None,
    )

    assert weather.temperature is None
    assert weather.humidity is None
    assert weather.precipitation is None
    assert weather.wind_speed is None
    assert weather.soil_temperature is None


def test_weather_data_distinguishes_missing_value_from_zero():
    weather = WeatherData(
        observed_at=datetime(2026, 8, 8, 15, 0),
        temperature=0.0,
        humidity=0.0,
        precipitation=0.0,
        wind_speed=0.0,
        soil_temperature=0.0,
    )

    assert weather.temperature == 0.0
    assert weather.temperature is not None

    assert weather.humidity == 0.0
    assert weather.humidity is not None

    assert weather.precipitation == 0.0
    assert weather.precipitation is not None

    assert weather.wind_speed == 0.0
    assert weather.wind_speed is not None

    assert weather.soil_temperature == 0.0
    assert weather.soil_temperature is not None


def test_weather_data_new_soil_fields_are_none_by_default():
    weather = WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
    )

    assert weather.soil_temperature_6cm is None
    assert weather.soil_temperature_18cm is None
    assert weather.soil_temperature_10cm_estimate is None


def test_weather_data_can_store_soil_temperatures_at_6_and_18_cm():
    weather = WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )

    assert weather.soil_temperature_6cm == 16.0
    assert weather.soil_temperature_18cm == 10.0


def test_weather_data_can_store_soil_temperature_estimate():
    estimate = SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(6.0, 18.0),
        source_temperatures=(16.0, 10.0),
        method=SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION,
    )

    weather = WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
        soil_temperature_10cm_estimate=estimate,
    )

    assert weather.soil_temperature_10cm_estimate == estimate

def test_weather_data_can_store_degree_days_result():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=15.0,
        ),
    )

    degree_days = DegreeDaysResult(
        base_temperature=10.0,
        total=7.0,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 2),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
        ),
    )

    weather = WeatherData(
        observed_at=datetime(2026, 8, 9, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        degree_days_10c=degree_days,
    )

    assert weather.degree_days_10c == degree_days