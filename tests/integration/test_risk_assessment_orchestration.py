from datetime import date, datetime, timedelta

import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.domain import (
    DailyTemperature,
    Location,
    RiskLevel,
    RiskStatus,
    UserProfile,
    WeatherData,
)
from app.integrations.weather import WeatherTimeoutError
from app.repositories import ThreatRepository
from app.risk import (
    RiskCalculatorRegistry,
    RiskContextPreparer,
    RiskEngine,
    RiskInputRequirements,
    RiskPolicy,
    SingleThreatRiskEvaluator,
)
from app.risk.calculators import (
    CabbageAphidRiskCalculator,
    CodlingMothRiskCalculator,
    ColoradoBeetleRiskCalculator,
    TickRiskCalculator,
)
from app.seed.threat_catalog import seed_threat_catalog
from app.services import (
    RiskAssessmentOrchestrator,
    ThreatService,
)
from app.weather import (
    DegreeDaysCalculator,
    SoilTemperatureEstimator,
)


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        seed_threat_catalog()

        yield app

        db.session.remove()
        db.drop_all()


class FakeWeatherService:
    def __init__(
        self,
        weather=None,
        error=None,
    ):
        self.weather = weather
        self.error = error
        self.calls = 0

    def get_current_weather(self, location):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.weather


class FakeHistoricalWeatherService:
    def __init__(
        self,
        observations=(),
        error=None,
    ):
        self.observations = observations
        self.error = error
        self.calls = 0
        self.received_start_date = None
        self.received_end_date = None

    def get_daily_temperatures(
        self,
        location,
        start_date,
        end_date,
    ):
        self.calls += 1
        self.received_start_date = start_date
        self.received_end_date = end_date

        if self.error is not None:
            raise self.error

        return self.observations


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_weather(
    *,
    temperature,
    humidity=None,
    soil_temperature_6cm=None,
    soil_temperature_18cm=None,
):
    return WeatherData(
        observed_at=datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        temperature=temperature,
        humidity=humidity,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=None,
        soil_temperature_6cm=soil_temperature_6cm,
        soil_temperature_18cm=soil_temperature_18cm,
    )


def create_historical_observations(
    *,
    days,
    mean_temperature,
):
    start_date = date(
        2026,
        5,
        1,
    )

    return tuple(
        DailyTemperature(
            date=start_date + timedelta(days=index),
            mean_temperature=mean_temperature,
        )
        for index in range(days)
    )


def create_orchestrator(
    *,
    weather_service,
    historical_weather_service,
):
    requirements = RiskInputRequirements()

    context_preparer = RiskContextPreparer(
        requirements=requirements,
        soil_temperature_estimator=(
            SoilTemperatureEstimator()
        ),
        degree_days_calculator=(
            DegreeDaysCalculator()
        ),
    )

    registry = RiskCalculatorRegistry(
        calculators={
            "TICK": TickRiskCalculator(),
            "COLORADO_BEETLE": (
                ColoradoBeetleRiskCalculator()
            ),
            "CABBAGE_APHID": (
                CabbageAphidRiskCalculator()
            ),
            "CODLING_MOTH": (
                CodlingMothRiskCalculator()
            ),
        },
    )

    evaluator = SingleThreatRiskEvaluator(
        context_preparer=context_preparer,
        calculator_registry=registry,
        engine=RiskEngine(
            policy=RiskPolicy(),
        ),
    )

    return RiskAssessmentOrchestrator(
        threat_service=ThreatService(
            ThreatRepository()
        ),
        weather_service=weather_service,
        historical_weather_service=(
            historical_weather_service
        ),
        input_requirements=requirements,
        evaluator=evaluator,
    )


def test_human_profile_runs_real_tick_calculation(app):
    with app.app_context():
        weather_service = FakeWeatherService(
            weather=create_weather(
                temperature=12.0,
                humidity=91.0,
            ),
        )

        historical_service = (
            FakeHistoricalWeatherService()
        )

        orchestrator = create_orchestrator(
            weather_service=weather_service,
            historical_weather_service=(
                historical_service
            ),
        )

        results = orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.HUMAN,
            assessment_date=date(
                2026,
                8,
                11,
            ),
        )

        assert len(results) == 1

        result = results[0]

        assert result.threat_code == "TICK"
        assert result.status == RiskStatus.CALCULATED
        assert result.risk_level == RiskLevel.HIGH

        assert weather_service.calls == 1
        assert historical_service.calls == 0


def test_vegetable_garden_reuses_current_weather_for_two_threats(
    app,
):
    with app.app_context():
        weather_service = FakeWeatherService(
            weather=create_weather(
                temperature=25.0,
                humidity=65.0,
                soil_temperature_6cm=16.0,
                soil_temperature_18cm=10.0,
            ),
        )

        historical_service = (
            FakeHistoricalWeatherService()
        )

        orchestrator = create_orchestrator(
            weather_service=weather_service,
            historical_weather_service=(
                historical_service
            ),
        )

        results = orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.VEGETABLE_GARDEN,
            assessment_date=date(
                2026,
                8,
                11,
            ),
        )

        results_by_code = {
            result.threat_code: result
            for result in results
        }

        assert set(results_by_code) == {
            "COLORADO_BEETLE",
            "CABBAGE_APHID",
        }

        colorado = results_by_code[
            "COLORADO_BEETLE"
        ]

        assert (
            colorado.status
            == RiskStatus.CALCULATED
        )
        assert (
            colorado.risk_level
            == RiskLevel.HIGH
        )
        assert (
            colorado.factors[0].actual_value
            == pytest.approx(14.0)
        )

        aphid = results_by_code[
            "CABBAGE_APHID"
        ]

        assert (
            aphid.status
            == RiskStatus.CALCULATED
        )
        assert (
            aphid.risk_level
            == RiskLevel.HIGH
        )

        assert weather_service.calls == 1
        assert historical_service.calls == 0


def test_garden_profile_runs_real_degree_days_calculation(
    app,
):
    with app.app_context():
        observations = create_historical_observations(
            days=13,
            mean_temperature=20.0,
        )

        weather_service = FakeWeatherService()

        historical_service = (
            FakeHistoricalWeatherService(
                observations=observations,
            )
        )

        orchestrator = create_orchestrator(
            weather_service=weather_service,
            historical_weather_service=(
                historical_service
            ),
        )

        results = orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.GARDEN,
            assessment_date=date(
                2026,
                8,
                11,
            ),
            historical_start_date=date(
                2026,
                5,
                1,
            ),
        )

        assert len(results) == 1

        result = results[0]

        assert result.threat_code == "CODLING_MOTH"
        assert result.status == RiskStatus.CALCULATED
        assert result.risk_level == RiskLevel.HIGH

        assert (
            result.factors[0].actual_value
            == pytest.approx(130.0)
        )

        assert weather_service.calls == 0
        assert historical_service.calls == 1

        assert (
            historical_service.received_start_date
            == date(
                2026,
                5,
                1,
            )
        )

        assert (
            historical_service.received_end_date
            == date(
                2026,
                8,
                11,
            )
        )


def test_weather_failure_produces_error_results_for_vegetable_garden(
    app,
):
    with app.app_context():
        weather_service = FakeWeatherService(
            error=WeatherTimeoutError(
                "Weather timeout."
            ),
        )

        historical_service = (
            FakeHistoricalWeatherService()
        )

        orchestrator = create_orchestrator(
            weather_service=weather_service,
            historical_weather_service=(
                historical_service
            ),
        )

        results = orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.VEGETABLE_GARDEN,
            assessment_date=date(
                2026,
                8,
                11,
            ),
        )

        assert {
            result.threat_code
            for result in results
        } == {
            "COLORADO_BEETLE",
            "CABBAGE_APHID",
        }

        assert all(
            result.status == RiskStatus.ERROR
            for result in results
        )

        assert all(
            result.risk_level is None
            for result in results
        )

        assert all(
            result.explanation == "Weather timeout."
            for result in results
        )

        assert weather_service.calls == 1
        assert historical_service.calls == 0