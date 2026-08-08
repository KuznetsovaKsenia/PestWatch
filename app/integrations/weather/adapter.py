from datetime import datetime

from app.domain import WeatherData
from app.integrations.weather.exceptions import WeatherDataError


class WeatherAdapter:
    def to_weather_data(
        self,
        payload: dict,
    ) -> WeatherData:
        current = payload.get("current")

        if not isinstance(current, dict):
            raise WeatherDataError(
                "Weather response does not contain current weather data."
            )

        observed_at_raw = current.get("time")

        if observed_at_raw is None:
            raise WeatherDataError(
                "Weather response does not contain observation time."
            )

        try:
            observed_at = datetime.fromisoformat(observed_at_raw)
        except (TypeError, ValueError) as exc:
            raise WeatherDataError(
                "Weather response contains invalid observation time."
            ) from exc

        return WeatherData(
            observed_at=observed_at,
            temperature=current.get("temperature_2m"),
            humidity=current.get("relative_humidity_2m"),
            precipitation=current.get("precipitation"),
            wind_speed=current.get("wind_speed_10m"),
            soil_temperature=current.get("soil_temperature_0cm"),
        )