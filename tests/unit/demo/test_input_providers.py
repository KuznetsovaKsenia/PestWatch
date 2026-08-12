from datetime import date

from app.demo import (
    DemoHistoricalWeatherService,
    DemoScenarioRegistry,
    DemoWeatherService,
)


def test_demo_weather_service_returns_fixture_weather():
    registry = DemoScenarioRegistry()
    scenario = registry.get("DEMO_C")
    service = DemoWeatherService(registry)

    weather = service.get_current_weather(
        scenario.location
    )

    assert weather is scenario.current_weather
    assert weather.temperature == 14.9
    assert weather.humidity == 50.0


def test_demo_weather_service_needs_no_external_client():
    registry = DemoScenarioRegistry()

    service = DemoWeatherService(registry)

    assert not hasattr(service, "_client")
    assert not hasattr(service, "_adapter")


def test_historical_service_returns_requested_period():
    registry = DemoScenarioRegistry()
    scenario = registry.get("DEMO_B")
    service = DemoHistoricalWeatherService(
        registry
    )

    observations = (
        service.get_daily_temperatures(
            scenario.location,
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 13),
        )
    )

    assert [
        observation.date
        for observation in observations
    ] == [
        date(2026, 5, 10),
        date(2026, 5, 11),
        date(2026, 5, 12),
        date(2026, 5, 13),
    ]

    assert [
        observation.mean_temperature
        for observation in observations
    ] == [
        20.0,
        20.0,
        20.0,
        19.9,
    ]


def test_historical_service_preserves_missing_temperature():
    registry = DemoScenarioRegistry()
    scenario = registry.get("DEMO_G")
    service = DemoHistoricalWeatherService(
        registry
    )

    observations = (
        service.get_daily_temperatures(
            scenario.location,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
        )
    )

    assert [
        observation.mean_temperature
        for observation in observations
    ] == [
        20.0,
        20.0,
        20.0,
        None,
        20.0,
    ]


def test_demo_historical_service_needs_no_external_client():
    registry = DemoScenarioRegistry()

    service = DemoHistoricalWeatherService(
        registry
    )

    assert not hasattr(service, "_client")
    assert not hasattr(service, "_adapter")
