import requests

from app.integrations.weather.exceptions import (
    WeatherConnectionError,
    WeatherResponseError,
    WeatherTimeoutError,
)


class WeatherClient:
    CURRENT_PARAMETERS = (
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
    )

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
    ):
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(self.CURRENT_PARAMETERS),
            "temperature_unit": "celsius",
            "wind_speed_unit": "ms",
            "precipitation_unit": "mm",
            "timezone": "auto",
        }

        try:
            response = requests.get(
                self._base_url,
                params=params,
                timeout=self._timeout_seconds,
            )

            response.raise_for_status()

            return response.json()

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

        except requests.JSONDecodeError as exc:
            raise WeatherResponseError(
                "Weather provider returned invalid JSON."
            ) from exc