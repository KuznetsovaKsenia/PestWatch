import pytest

from app.domain import Location
from app.services import (
    LocationNotFoundError,
    LocationService,
)


class FakeGeocodingClient:
    def __init__(self, payload):
        self.payload = payload
        self.received_name = None

    def search_locations(self, name):
        self.received_name = name
        return self.payload


class FakeGeocodingAdapter:
    def __init__(self, location):
        self.location = location
        self.received = None

    def to_location(self, payload, **kwargs):
        self.received = (payload, kwargs)
        return self.location


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def test_service_resolves_location():
    payload = {"results": []}
    client = FakeGeocodingClient(payload)
    adapter = FakeGeocodingAdapter(create_location())

    service = LocationService(
        client=client,
        adapter=adapter,
    )

    result = service.resolve(
        name=" Москва ",
        region=" Москва ",
        country=" Россия ",
    )

    assert result == create_location()
    assert client.received_name == "Москва"
    assert adapter.received == (
        payload,
        {
            "requested_name": "Москва",
            "requested_region": "Москва",
            "requested_country": "Россия",
        },
    )


def test_service_raises_not_found_when_adapter_has_no_match():
    service = LocationService(
        client=FakeGeocodingClient({"results": []}),
        adapter=FakeGeocodingAdapter(None),
    )

    with pytest.raises(LocationNotFoundError):
        service.resolve(
            name="Москва",
            region="Москва",
            country="Россия",
        )


@pytest.mark.parametrize(
    ("name", "region", "country"),
    [
        ("", "Москва", "Россия"),
        ("Москва", "", "Россия"),
        ("Москва", "Москва", ""),
    ],
)
def test_service_rejects_empty_location_fields(
    name,
    region,
    country,
):
    service = LocationService(
        client=FakeGeocodingClient({}),
        adapter=FakeGeocodingAdapter(None),
    )

    with pytest.raises(ValueError):
        service.resolve(
            name=name,
            region=region,
            country=country,
        )
