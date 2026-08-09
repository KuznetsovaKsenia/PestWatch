from app.domain import Location, WeatherData
from app.integrations.weather import (
    WeatherAdapter,
    WeatherClient,
)


class WeatherService:
    def __init__(
        self,
        client: WeatherClient,
        adapter: WeatherAdapter,
    ):
        self._client = client
        self._adapter = adapter

    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        payload = self._client.get_current_weather(
            latitude=location.latitude,
            longitude=location.longitude,
        )

        return self._adapter.to_weather_data(payload)