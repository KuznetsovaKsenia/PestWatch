from app.demo.scenario_registry import DemoScenarioRegistry
from app.domain import Location, WeatherData


class DemoWeatherService:
    def __init__(
        self,
        registry: DemoScenarioRegistry,
    ):
        self._registry = registry

    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        return (
            self._registry
            .find_by_location(location)
            .current_weather
        )
