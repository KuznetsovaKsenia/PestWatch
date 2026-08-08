import pytest

from app.domain import Location


def test_location_can_be_created():
    location = Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )

    assert location.name == "Москва"
    assert location.region == "Москва"
    assert location.country == "Россия"
    assert location.latitude == 55.7558
    assert location.longitude == 37.6173


def test_location_allows_missing_region():
    location = Location(
        name="Москва",
        region=None,
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )

    assert location.region is None


@pytest.mark.parametrize("latitude", [-90, 90])
def test_location_accepts_boundary_latitude(latitude):
    location = Location(
        name="Test",
        region=None,
        country="Россия",
        latitude=latitude,
        longitude=0,
    )

    assert location.latitude == latitude


@pytest.mark.parametrize("longitude", [-180, 180])
def test_location_accepts_boundary_longitude(longitude):
    location = Location(
        name="Test",
        region=None,
        country="Россия",
        latitude=0,
        longitude=longitude,
    )

    assert location.longitude == longitude


@pytest.mark.parametrize("latitude", [-90.1, 90.1])
def test_location_rejects_invalid_latitude(latitude):
    with pytest.raises(
        ValueError,
        match="Latitude must be between -90 and 90 degrees",
    ):
        Location(
            name="Test",
            region=None,
            country="Россия",
            latitude=latitude,
            longitude=0,
        )


@pytest.mark.parametrize("longitude", [-180.1, 180.1])
def test_location_rejects_invalid_longitude(longitude):
    with pytest.raises(
        ValueError,
        match="Longitude must be between -180 and 180 degrees",
    ):
        Location(
            name="Test",
            region=None,
            country="Россия",
            latitude=0,
            longitude=longitude,
        )