import pytest

from app.domain import Location
from app.integrations.geocoding import (
    GeocodingDataError,
    OpenMeteoGeocodingAdapter,
)


def test_adapter_returns_matching_location():
    payload = {
        "results": [
            {
                "name": "Москва",
                "admin1": "Москва",
                "country": "Россия",
                "latitude": 55.7558,
                "longitude": 37.6173,
            }
        ]
    }

    result = OpenMeteoGeocodingAdapter().to_location(
        payload,
        requested_name="Москва",
        requested_region="Москва",
        requested_country="Россия",
    )

    assert result == Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def test_adapter_prefers_exact_name_within_region_and_country():
    payload = {
        "results": [
            {
                "name": "Московский",
                "admin1": "Москва",
                "country": "Россия",
                "latitude": 55.6,
                "longitude": 37.3,
            },
            {
                "name": "Москва",
                "admin1": "Москва",
                "country": "Россия",
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
        ]
    }

    result = OpenMeteoGeocodingAdapter().to_location(
        payload,
        requested_name="Москва",
        requested_region="Москва",
        requested_country="Россия",
    )

    assert result.name == "Москва"
    assert result.latitude == 55.7558


def test_adapter_rejects_other_region_or_country():
    payload = {
        "results": [
            {
                "name": "Москва",
                "admin1": "Другая область",
                "country": "Россия",
                "latitude": 50.0,
                "longitude": 40.0,
            },
            {
                "name": "Москва",
                "admin1": "Москва",
                "country": "Другая страна",
                "latitude": 51.0,
                "longitude": 41.0,
            },
        ]
    }

    result = OpenMeteoGeocodingAdapter().to_location(
        payload,
        requested_name="Москва",
        requested_region="Москва",
        requested_country="Россия",
    )

    assert result is None


def test_adapter_returns_none_when_results_are_absent():
    result = OpenMeteoGeocodingAdapter().to_location(
        {},
        requested_name="Москва",
        requested_region="Москва",
        requested_country="Россия",
    )

    assert result is None


def test_adapter_rejects_invalid_results_structure():
    with pytest.raises(GeocodingDataError):
        OpenMeteoGeocodingAdapter().to_location(
            {"results": "invalid"},
            requested_name="Москва",
            requested_region="Москва",
            requested_country="Россия",
        )
