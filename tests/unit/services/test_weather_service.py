from datetime import datetime

from app.domain import (
    Location,
    WeatherData,
)
from app.services import WeatherService


class FakeWeatherClient:
    def __init__(self, payload):
        self.payload = payload
        self.received_latitude = None
        self.received_longitude = None

    def get_current_weather(
        self,
        latitude,
        longitude,
    ):
        self.received_latitude = latitude
        self.received_longitude = longitude

        return self.payload


class FakeWeatherAdapter:
    def __init__(self, weather_data):
        self.weather_data = weather_data
        self.received_payload = None

    def to_weather_data(self, payload):
        self.received_payload = payload

        return self.weather_data


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_weather_data():
    return WeatherData(
        observed_at=datetime(2026, 8, 8, 19, 0),
        temperature=18.4,
        humidity=67.0,
        precipitation=0.0,
        wind_speed=3.2,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )


def test_service_passes_location_coordinates_to_client():
    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        create_weather_data(),
    )

    service = WeatherService(
        client=client,
        adapter=adapter,
    )

    service.get_current_weather(
        create_location(),
    )

    assert client.received_latitude == 55.7558
    assert client.received_longitude == 37.6173


def test_service_passes_client_payload_to_adapter():
    payload = {
        "current": {
            "time": "2026-08-08T19:00",
        }
    }

    client = FakeWeatherClient(payload)
    adapter = FakeWeatherAdapter(
        create_weather_data(),
    )

    service = WeatherService(
        client=client,
        adapter=adapter,
    )

    service.get_current_weather(
        create_location(),
    )

    assert adapter.received_payload is payload


def test_service_returns_weather_data_from_adapter():
    weather_data = create_weather_data()

    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        weather_data,
    )

    service = WeatherService(
        client=client,
        adapter=adapter,
    )

    result = service.get_current_weather(
        create_location(),
    )

    assert result is weather_data