from datetime import date

from app.domain import DailyTemperature
from app.integrations.weather.exceptions import WeatherDataError


class HistoricalWeatherAdapter:
    def to_daily_temperatures(
        self,
        payload: dict,
    ) -> tuple[DailyTemperature, ...]:
        daily = payload.get("daily")

        if not isinstance(daily, dict):
            raise WeatherDataError(
                "Historical weather response does not contain daily data."
            )

        dates = daily.get("time")
        temperatures = daily.get("temperature_2m_mean")

        if not isinstance(dates, list):
            raise WeatherDataError(
                "Historical weather response does not contain daily dates."
            )

        if not isinstance(temperatures, list):
            raise WeatherDataError(
                "Historical weather response does not contain "
                "daily mean temperatures."
            )

        if len(dates) != len(temperatures):
            raise WeatherDataError(
                "Historical weather response contains arrays "
                "with different lengths."
            )

        observations = []

        for raw_date, temperature in zip(
            dates,
            temperatures,
        ):
            try:
                observation_date = date.fromisoformat(raw_date)
            except (TypeError, ValueError) as exc:
                raise WeatherDataError(
                    "Historical weather response contains invalid date."
                ) from exc

            observations.append(
                DailyTemperature(
                    date=observation_date,
                    mean_temperature=temperature,
                )
            )

        return tuple(observations)