from datetime import datetime

import pytest

from app.domain import WeatherData
from app.integrations.weather import (
    WeatherAdapter,
    WeatherDataError,
)


def test_adapter_maps_complete_payload():
    payload = {
        "current": {
            "time": "2026-08-08T19:00",
            "temperature_2m": 18.4,
            "relative_humidity_2m": 67.0,
            "precipitation": 1.2,
            "wind_speed_10m": 3.2,
            "soil_temperature_0cm": 16.1,
        }
    }

    adapter = WeatherAdapter()

    weather = adapter.to_weather_data(payload)

    assert isinstance(weather, WeatherData)

    assert weather.observed_at == datetime(
        2026,
        8,
        8,
        19,
        0,
    )
    assert weather.temperature == 18.4
    assert weather.humidity == 67.0
    assert weather.precipitation == 1.2
    assert weather.wind_speed == 3.2
    assert weather.soil_temperature == 16.1


def test_adapter_maps_missing_optional_values_to_none():
    payload = {
        "current": {
            "time": "2026-08-08T19:00",
            "temperature_2m": 18.4,
        }
    }

    adapter = WeatherAdapter()

    weather = adapter.to_weather_data(payload)

    assert weather.temperature == 18.4
    assert weather.humidity is None
    assert weather.precipitation is None
    assert weather.wind_speed is None
    assert weather.soil_temperature is None


def test_adapter_preserves_zero_values():
    payload = {
        "current": {
            "time": "2026-08-08T19:00",
            "temperature_2m": 0.0,
            "relative_humidity_2m": 0.0,
            "precipitation": 0.0,
            "wind_speed_10m": 0.0,
            "soil_temperature_0cm": 0.0,
        }
    }

    adapter = WeatherAdapter()

    weather = adapter.to_weather_data(payload)

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


def test_adapter_rejects_missing_current():
    adapter = WeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="does not contain current weather data",
    ):
        adapter.to_weather_data({})


def test_adapter_rejects_missing_observation_time():
    payload = {
        "current": {
            "temperature_2m": 18.4,
        }
    }

    adapter = WeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="does not contain observation time",
    ):
        adapter.to_weather_data(payload)


@pytest.mark.parametrize(
    "invalid_time",
    [
        "not-a-date",
        123,
        [],
    ],
)
def test_adapter_rejects_invalid_observation_time(
    invalid_time,
):
    payload = {
        "current": {
            "time": invalid_time,
        }
    }

    adapter = WeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="contains invalid observation time",
    ):
        adapter.to_weather_data(payload)