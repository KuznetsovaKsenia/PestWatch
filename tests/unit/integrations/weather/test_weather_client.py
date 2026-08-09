from unittest.mock import Mock, patch

import pytest
import requests

from app.integrations.weather import (
    WeatherClient,
    WeatherConnectionError,
    WeatherResponseError,
    WeatherTimeoutError,
)


BASE_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 5


def create_client():
    return WeatherClient(
        base_url=BASE_URL,
        timeout_seconds=TIMEOUT,
    )


@patch("app.integrations.weather.client.requests.get")
def test_client_sends_expected_request(mock_get):
    response = Mock()
    response.json.return_value = {
        "current": {
            "time": "2026-08-08T19:00",
        }
    }

    mock_get.return_value = response

    client = create_client()

    client.get_current_weather(
        latitude=55.7558,
        longitude=37.6173,
    )

    mock_get.assert_called_once_with(
        BASE_URL,
        params={
            "latitude": 55.7558,
            "longitude": 37.6173,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m,"
                "soil_temperature_0cm,"
                "soil_temperature_6cm,"
                "soil_temperature_18cm"
            ),
            "temperature_unit": "celsius",
            "wind_speed_unit": "ms",
            "precipitation_unit": "mm",
            "timezone": "auto",
        },
        timeout=TIMEOUT,
    )


@patch("app.integrations.weather.client.requests.get")
def test_client_returns_json_payload(mock_get):
    payload = {
        "current": {
            "time": "2026-08-08T19:00",
            "temperature_2m": 18.4,
        }
    }

    response = Mock()
    response.json.return_value = payload

    mock_get.return_value = response

    client = create_client()

    result = client.get_current_weather(
        latitude=55.7558,
        longitude=37.6173,
    )

    assert result == payload


@patch("app.integrations.weather.client.requests.get")
def test_client_raises_timeout_error(mock_get):
    mock_get.side_effect = requests.Timeout()

    client = create_client()

    with pytest.raises(
        WeatherTimeoutError,
        match="Weather provider request timed out",
    ):
        client.get_current_weather(
            latitude=55.7558,
            longitude=37.6173,
        )


@patch("app.integrations.weather.client.requests.get")
def test_client_raises_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError()

    client = create_client()

    with pytest.raises(
        WeatherConnectionError,
        match="Could not connect to weather provider",
    ):
        client.get_current_weather(
            latitude=55.7558,
            longitude=37.6173,
        )


@patch("app.integrations.weather.client.requests.get")
def test_client_raises_response_error_for_http_error(mock_get):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError()

    mock_get.return_value = response

    client = create_client()

    with pytest.raises(
        WeatherResponseError,
        match="Weather provider returned an HTTP error",
    ):
        client.get_current_weather(
            latitude=55.7558,
            longitude=37.6173,
        )


@patch("app.integrations.weather.client.requests.get")
def test_client_raises_response_error_for_invalid_json(mock_get):
    response = Mock()

    response.json.side_effect = requests.JSONDecodeError(
        "Invalid JSON",
        "",
        0,
    )

    mock_get.return_value = response

    client = create_client()

    with pytest.raises(
        WeatherResponseError,
        match="Weather provider returned invalid JSON",
    ):
        client.get_current_weather(
            latitude=55.7558,
            longitude=37.6173,
        )