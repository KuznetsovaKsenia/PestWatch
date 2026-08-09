from datetime import date

import requests

from app.integrations.weather.exceptions import (
    WeatherConnectionError,
    WeatherResponseError,
    WeatherTimeoutError,
)


class HistoricalWeatherClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: int,
    ):
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def get_daily_mean_temperatures(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_mean",
            "temperature_unit": "celsius",
            "timezone": "auto",
        }

        try:
            response = requests.get(
                self._base_url,
                params=params,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise WeatherTimeoutError(
                "Weather provider request timed out."
            ) from exc
        except requests.ConnectionError as exc:
            raise WeatherConnectionError(
                "Could not connect to weather provider."
            ) from exc
        except requests.HTTPError as exc:
            raise WeatherResponseError(
                "Weather provider returned an HTTP error."
            ) from exc

        try:
            return response.json()
        except requests.JSONDecodeError as exc:
            raise WeatherResponseError(
                "Weather provider returned invalid JSON."
            ) from exc