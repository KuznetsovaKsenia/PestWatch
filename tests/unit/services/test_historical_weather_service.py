from datetime import date

from app.domain import DailyTemperature, Location
from app.services import HistoricalWeatherService


class FakeHistoricalWeatherClient:
    def __init__(self, payload):
        self.payload = payload
        self.received_latitude = None
        self.received_longitude = None
        self.received_start_date = None
        self.received_end_date = None

    def get_daily_mean_temperatures(
        self,
        latitude,
        longitude,
        start_date,
        end_date,
    ):
        self.received_latitude = latitude
        self.received_longitude = longitude
        self.received_start_date = start_date
        self.received_end_date = end_date

        return self.payload


class FakeHistoricalWeatherAdapter:
    def __init__(self, observations):
        self.observations = observations
        self.received_payload = None

    def to_daily_temperatures(self, payload):
        self.received_payload = payload

        return self.observations


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_observations():
    return (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.5,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=14.0,
        ),
    )


def test_service_passes_location_coordinates_to_client():
    client = FakeHistoricalWeatherClient(
        payload={"daily": {}},
    )
    adapter = FakeHistoricalWeatherAdapter(
        create_observations(),
    )

    service = HistoricalWeatherService(
        client=client,
        adapter=adapter,
    )

    service.get_daily_temperatures(
        location=create_location(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    assert client.received_latitude == 55.7558
    assert client.received_longitude == 37.6173


def test_service_passes_date_range_to_client():
    client = FakeHistoricalWeatherClient(
        payload={"daily": {}},
    )
    adapter = FakeHistoricalWeatherAdapter(
        create_observations(),
    )

    service = HistoricalWeatherService(
        client=client,
        adapter=adapter,
    )

    service.get_daily_temperatures(
        location=create_location(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    assert client.received_start_date == date(2026, 1, 1)
    assert client.received_end_date == date(2026, 8, 8)


def test_service_passes_client_payload_to_adapter():
    payload = {
        "daily": {
            "time": ["2026-05-01"],
            "temperature_2m_mean": [12.5],
        }
    }

    client = FakeHistoricalWeatherClient(payload)
    adapter = FakeHistoricalWeatherAdapter(
        create_observations(),
    )

    service = HistoricalWeatherService(
        client=client,
        adapter=adapter,
    )

    service.get_daily_temperatures(
        location=create_location(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    assert adapter.received_payload is payload


def test_service_returns_observations_from_adapter():
    observations = create_observations()

    client = FakeHistoricalWeatherClient(
        payload={"daily": {}},
    )
    adapter = FakeHistoricalWeatherAdapter(
        observations,
    )

    service = HistoricalWeatherService(
        client=client,
        adapter=adapter,
    )

    result = service.get_daily_temperatures(
        location=create_location(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 8),
    )

    assert result is observations