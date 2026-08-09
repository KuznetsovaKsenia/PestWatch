from dataclasses import replace

from app.domain import Location, WeatherData
from app.integrations.weather import (
    WeatherAdapter,
    WeatherClient,
)
from app.weather import SoilTemperatureEstimator


class WeatherService:
    def __init__(
        self,
        client: WeatherClient,
        adapter: WeatherAdapter,
        soil_temperature_estimator: SoilTemperatureEstimator,
    ):
        self._client = client
        self._adapter = adapter
        self._soil_temperature_estimator = (
            soil_temperature_estimator
        )

    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        payload = self._client.get_current_weather(
            latitude=location.latitude,
            longitude=location.longitude,
        )

        weather = self._adapter.to_weather_data(payload)

        estimate = (
            self._soil_temperature_estimator.estimate_at_10cm(
                temperature_6cm=weather.soil_temperature_6cm,
                temperature_18cm=weather.soil_temperature_18cm,
            )
        )

        if estimate is None:
            return weather

        return replace(
            weather,
            soil_temperature_10cm_estimate=estimate,
        )