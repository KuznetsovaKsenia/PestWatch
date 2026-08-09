from datetime import date
from unittest.mock import Mock, patch

import pytest
import requests

from app.integrations.weather import (
    HistoricalWeatherClient,
    WeatherConnectionError,
    WeatherResponseError,
    WeatherTimeoutError,
)


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
TIMEOUT = 5


def create_client():
    return HistoricalWeatherClient(
        base_url=BASE_URL,
        timeout_seconds=TIMEOUT,
    )


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_sends_expected_request(mock_get):
    response = Mock()
    response.json.return_value = {
        "daily": {
            "time": [],
            "temperature_2m_mean": [],
        }
    }

    mock_get.return_value = response

    client = create_client()

    client.get_daily_mean_temperatures(
        latitude=55.7558,
        longitude=37.6173,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    mock_get.assert_called_once_with(
        BASE_URL,
        params={
            "latitude": 55.7558,
            "longitude": 37.6173,
            "start_date": "2026-01-01",
            "end_date": "2026-08-08",
            "daily": "temperature_2m_mean",
            "temperature_unit": "celsius",
            "timezone": "auto",
        },
        timeout=TIMEOUT,
    )


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_returns_json_payload(mock_get):
    payload = {
        "daily": {
            "time": [
                "2026-05-01",
                "2026-05-02",
            ],
            "temperature_2m_mean": [
                12.5,
                14.0,
            ],
        }
    }

    response = Mock()
    response.json.return_value = payload

    mock_get.return_value = response

    client = create_client()

    result = client.get_daily_mean_temperatures(
        latitude=55.7558,
        longitude=37.6173,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    assert result == payload


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_raises_timeout_error(mock_get):
    mock_get.side_effect = requests.Timeout()

    client = create_client()

    with pytest.raises(
        WeatherTimeoutError,
        match="Weather provider request timed out",
    ):
        client.get_daily_mean_temperatures(
            latitude=55.7558,
            longitude=37.6173,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 8, 8),
        )


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_raises_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError()

    client = create_client()

    with pytest.raises(
        WeatherConnectionError,
        match="Could not connect to weather provider",
    ):
        client.get_daily_mean_temperatures(
            latitude=55.7558,
            longitude=37.6173,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 8, 8),
        )


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_raises_response_error_for_http_error(
    mock_get,
):
    response = Mock()
    response.raise_for_status.side_effect = (
        requests.HTTPError()
    )

    mock_get.return_value = response

    client = create_client()

    with pytest.raises(
        WeatherResponseError,
        match="Weather provider returned an HTTP error",
    ):
        client.get_daily_mean_temperatures(
            latitude=55.7558,
            longitude=37.6173,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 8, 8),
        )


@patch(
    "app.integrations.weather.historical_client.requests.get"
)
def test_client_raises_response_error_for_invalid_json(
    mock_get,
):
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
        client.get_daily_mean_temperatures(
            latitude=55.7558,
            longitude=37.6173,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 8, 8),
        )