from datetime import date, datetime, timedelta

from app.bootstrap import build_assessment_services
from app.domain import (
    DailyTemperature,
    Location,
    WeatherData,
)


class DeterministicLocationService:
    """
    Deterministic replacement for the external
    geocoding boundary used by REAL E2E tests.

    It preserves the LocationService public contract,
    but performs no external HTTP requests.
    """

    def resolve(
        self,
        *,
        name: str,
        region: str,
        country: str,
    ) -> Location:
        return Location(
            name=name.strip(),
            region=region.strip(),
            country=country.strip(),
            latitude=54.5138,
            longitude=36.2612,
        )


class DeterministicWeatherService:
    """
    Deterministic replacement for the current
    weather integration boundary.
    """

    def get_current_weather(
        self,
        location: Location,
    ) -> WeatherData:
        return WeatherData(
            observed_at=datetime(
                2026,
                8,
                13,
                12,
                0,
            ),
            temperature=18.0,
            humidity=80.0,
            precipitation=0.0,
            wind_speed=2.0,
            soil_temperature=15.0,
            soil_temperature_6cm=16.0,
            soil_temperature_18cm=13.0,
        )


class DeterministicHistoricalWeatherService:
    """
    Deterministic replacement for the Open-Meteo
    archive boundary.

    It returns one observation for every requested
    calendar day, so the orchestrator can use its
    normal period-selection and degree-day logic.
    """

    def get_daily_temperatures(
        self,
        location: Location,
        start_date: date,
        end_date: date,
    ) -> tuple[DailyTemperature, ...]:
        observations = []

        current_date = start_date

        while current_date <= end_date:
            observations.append(
                DailyTemperature(
                    date=current_date,
                    mean_temperature=18.0,
                )
            )

            current_date += timedelta(
                days=1
            )

        return tuple(observations)


def build_deterministic_assessment_services(
    config,
):
    """
    Build the normal PestWatch application graph,
    then replace only external REAL-data boundaries.

    Preserved:
    - controllers;
    - AssessmentExecutionService;
    - RiskAssessmentOrchestrator;
    - risk calculators;
    - AssessmentService;
    - AssessmentRepository;
    - SQLite persistence;
    - Demo Mode infrastructure.

    Replaced:
    - geocoding HTTP boundary;
    - current weather HTTP boundary;
    - historical weather HTTP boundary.
    """

    (
        execution_service,
        history_service,
        _,
    ) = build_assessment_services(
        config
    )

    real_orchestrator = (
        execution_service._orchestrator
    )

    real_orchestrator._weather_service = (
        DeterministicWeatherService()
    )

    real_orchestrator._historical_weather_service = (
        DeterministicHistoricalWeatherService()
    )

    location_service = (
        DeterministicLocationService()
    )

    return (
        execution_service,
        history_service,
        location_service,
    )