from app.domain import Location
from app.integrations.geocoding import (
    OpenMeteoGeocodingAdapter,
    OpenMeteoGeocodingClient,
)


class LocationNotFoundError(Exception):
    """Requested user location could not be resolved."""


class LocationService:
    def __init__(
        self,
        client: OpenMeteoGeocodingClient,
        adapter: OpenMeteoGeocodingAdapter,
    ):
        self._client = client
        self._adapter = adapter

    def resolve(
        self,
        *,
        name: str,
        region: str,
        country: str,
    ) -> Location:
        normalized_name = name.strip()
        normalized_region = region.strip()
        normalized_country = country.strip()

        if not all(
            (
                normalized_name,
                normalized_region,
                normalized_country,
            )
        ):
            raise ValueError(
                "Location fields must not be empty."
            )

        payload = self._client.search_locations(
            normalized_name
        )

        location = self._adapter.to_location(
            payload,
            requested_name=normalized_name,
            requested_region=normalized_region,
            requested_country=normalized_country,
        )

        if location is None:
            raise LocationNotFoundError(
                "Requested location was not found."
            )

        return location
