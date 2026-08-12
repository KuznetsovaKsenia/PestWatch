from datetime import date

from app.demo.scenario_registry import DemoScenarioRegistry
from app.domain import DailyTemperature, Location


class DemoHistoricalWeatherService:
    def __init__(
        self,
        registry: DemoScenarioRegistry,
    ):
        self._registry = registry

    def get_daily_temperatures(
        self,
        location: Location,
        start_date: date,
        end_date: date,
    ) -> tuple[DailyTemperature, ...]:
        scenario = self._registry.find_by_location(
            location
        )

        return tuple(
            observation
            for observation
            in scenario.historical_temperatures
            if (
                start_date
                <= observation.date
                <= end_date
            )
        )
