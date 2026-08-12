from app.domain import Location
from app.integrations.geocoding.exceptions import GeocodingDataError


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


class OpenMeteoGeocodingAdapter:
    def to_location(
        self,
        payload: dict,
        *,
        requested_name: str,
        requested_region: str,
        requested_country: str,
    ) -> Location | None:
        results = payload.get("results")

        if results is None:
            return None

        if not isinstance(results, list):
            raise GeocodingDataError(
                "Geocoding response contains invalid results."
            )

        requested_name_normalized = _normalize(requested_name)
        requested_region_normalized = _normalize(requested_region)
        requested_country_normalized = _normalize(requested_country)

        matching_locations: list[tuple[bool, dict]] = []

        for candidate in results:
            if not isinstance(candidate, dict):
                continue

            name = candidate.get("name")
            region = candidate.get("admin1")
            country = candidate.get("country")
            latitude = candidate.get("latitude")
            longitude = candidate.get("longitude")

            if not all(
                isinstance(value, str) and value.strip()
                for value in (name, region, country)
            ):
                continue

            if not isinstance(latitude, (int, float)):
                continue

            if not isinstance(longitude, (int, float)):
                continue

            if _normalize(country) != requested_country_normalized:
                continue

            if _normalize(region) != requested_region_normalized:
                continue

            exact_name = (
                _normalize(name)
                == requested_name_normalized
            )

            matching_locations.append(
                (exact_name, candidate)
            )

        if not matching_locations:
            return None

        matching_locations.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        selected = matching_locations[0][1]

        try:
            return Location(
                name=selected["name"].strip(),
                region=selected["admin1"].strip(),
                country=selected["country"].strip(),
                latitude=float(selected["latitude"]),
                longitude=float(selected["longitude"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GeocodingDataError(
                "Geocoding response contains invalid location data."
            ) from exc
