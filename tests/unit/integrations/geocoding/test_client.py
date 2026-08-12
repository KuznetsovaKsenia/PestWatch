from unittest.mock import Mock, patch

import pytest
import requests

from app.integrations.geocoding import (
    GeocodingConnectionError,
    GeocodingResponseError,
    GeocodingTimeoutError,
    OpenMeteoGeocodingClient,
)


BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
TIMEOUT = 5


def create_client():
    return OpenMeteoGeocodingClient(
        base_url=BASE_URL,
        timeout_seconds=TIMEOUT,
    )


@patch("app.integrations.geocoding.client.requests.get")
def test_client_sends_expected_request(mock_get):
    response = Mock()
    response.json.return_value = {"results": []}
    mock_get.return_value = response

    client = create_client()

    client.search_locations("Москва")

    mock_get.assert_called_once_with(
        BASE_URL,
        params={
            "name": "Москва",
            "count": 10,
            "language": "ru",
            "format": "json",
        },
        timeout=TIMEOUT,
    )


@patch("app.integrations.geocoding.client.requests.get")
def test_client_returns_json_payload(mock_get):
    payload = {"results": [{"name": "Москва"}]}

    response = Mock()
    response.json.return_value = payload
    mock_get.return_value = response

    result = create_client().search_locations("Москва")

    assert result == payload


@patch("app.integrations.geocoding.client.requests.get")
def test_client_raises_timeout_error(mock_get):
    mock_get.side_effect = requests.Timeout()

    with pytest.raises(GeocodingTimeoutError):
        create_client().search_locations("Москва")


@patch("app.integrations.geocoding.client.requests.get")
def test_client_raises_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError()

    with pytest.raises(GeocodingConnectionError):
        create_client().search_locations("Москва")


@patch("app.integrations.geocoding.client.requests.get")
def test_client_raises_response_error_for_http_error(mock_get):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError()
    mock_get.return_value = response

    with pytest.raises(GeocodingResponseError):
        create_client().search_locations("Москва")


@patch("app.integrations.geocoding.client.requests.get")
def test_client_raises_response_error_for_invalid_json(mock_get):
    response = Mock()
    response.json.side_effect = requests.JSONDecodeError(
        "Invalid JSON",
        "",
        0,
    )
    mock_get.return_value = response

    with pytest.raises(GeocodingResponseError):
        create_client().search_locations("Москва")
