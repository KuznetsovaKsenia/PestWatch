from datetime import datetime

from app.domain import WeatherData


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