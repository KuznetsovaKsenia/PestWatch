from datetime import date

from app.domain import DailyTemperature, Location
from app.integrations.weather import (
    HistoricalWeatherAdapter,
    HistoricalWeatherClient,
)


class HistoricalWeatherService:
    def __init__(
        self,
        client: HistoricalWeatherClient,
        adapter: HistoricalWeatherAdapter,
    ):
        self._client = client
        self._adapter = adapter

    def get_daily_temperatures(
        self,
        location: Location,
        start_date: date,
        end_date: date,
    ) -> tuple[DailyTemperature, ...]:
        payload = self._client.get_daily_mean_temperatures(
            latitude=location.latitude,
            longitude=location.longitude,
            start_date=start_date,
            end_date=end_date,
        )

        return self._adapter.to_daily_temperatures(payload)