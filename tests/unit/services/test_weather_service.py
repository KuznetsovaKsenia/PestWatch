from datetime import datetime

from app.domain import (
    Location,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
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


class FakeSoilTemperatureEstimator:
    def __init__(self, estimate=None):
        self.estimate = estimate
        self.received_temperature_6cm = None
        self.received_temperature_18cm = None

    def estimate_at_10cm(
        self,
        temperature_6cm,
        temperature_18cm,
    ):
        self.received_temperature_6cm = temperature_6cm
        self.received_temperature_18cm = temperature_18cm

        return self.estimate


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


def create_estimate():
    return SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(6.0, 18.0),
        source_temperatures=(16.0, 10.0),
        method=(
            SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
        ),
    )


def test_service_passes_location_coordinates_to_client():
    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        create_weather_data(),
    )
    estimator = FakeSoilTemperatureEstimator()

    service = WeatherService(
        client=client,
        adapter=adapter,
        soil_temperature_estimator=estimator,
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
    estimator = FakeSoilTemperatureEstimator()

    service = WeatherService(
        client=client,
        adapter=adapter,
        soil_temperature_estimator=estimator,
    )

    service.get_current_weather(
        create_location(),
    )

    assert adapter.received_payload is payload


def test_service_returns_weather_data_when_estimate_is_unavailable():
    weather_data = create_weather_data()

    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        weather_data,
    )
    estimator = FakeSoilTemperatureEstimator(
        estimate=None,
    )

    service = WeatherService(
        client=client,
        adapter=adapter,
        soil_temperature_estimator=estimator,
    )

    result = service.get_current_weather(
        create_location(),
    )

    assert result is weather_data
    assert result.soil_temperature_10cm_estimate is None


def test_service_passes_soil_temperatures_to_estimator():
    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        create_weather_data(),
    )
    estimator = FakeSoilTemperatureEstimator()

    service = WeatherService(
        client=client,
        adapter=adapter,
        soil_temperature_estimator=estimator,
    )

    service.get_current_weather(
        create_location(),
    )

    assert estimator.received_temperature_6cm == 16.0
    assert estimator.received_temperature_18cm == 10.0


def test_service_adds_soil_temperature_estimate_to_weather_data():
    estimate = create_estimate()

    client = FakeWeatherClient(
        payload={"current": {}},
    )
    adapter = FakeWeatherAdapter(
        create_weather_data(),
    )
    estimator = FakeSoilTemperatureEstimator(
        estimate=estimate,
    )

    service = WeatherService(
        client=client,
        adapter=adapter,
        soil_temperature_estimator=estimator,
    )

    result = service.get_current_weather(
        create_location(),
    )

    assert result.soil_temperature_10cm_estimate == estimate

    assert result.soil_temperature_6cm == 16.0
    assert result.soil_temperature_18cm == 10.0