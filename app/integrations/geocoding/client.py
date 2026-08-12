import requests

from app.integrations.geocoding.exceptions import (
    GeocodingConnectionError,
    GeocodingResponseError,
    GeocodingTimeoutError,
)


class OpenMeteoGeocodingClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
    ):
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def search_locations(
        self,
        name: str,
    ) -> dict:
        params = {
            "name": name,
            "count": 10,
            "language": "ru",
            "format": "json",
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
            raise GeocodingTimeoutError(
                "Geocoding provider request timed out."
            ) from exc

        except requests.ConnectionError as exc:
            raise GeocodingConnectionError(
                "Could not connect to geocoding provider."
            ) from exc

        except requests.HTTPError as exc:
            raise GeocodingResponseError(
                "Geocoding provider returned an HTTP error."
            ) from exc

        except requests.JSONDecodeError as exc:
            raise GeocodingResponseError(
                "Geocoding provider returned invalid JSON."
            ) from exc
