from dataclasses import dataclass
from datetime import date, datetime

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    RiskInputCapability,
    RiskLevel,
    RiskResult,
    RiskStatus,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    Threat,
    UserProfile,
    WeatherData,
)
from app.integrations.weather import (
    WeatherTimeoutError,
)
from app.services import (
    RiskAssessmentOrchestrator,
)


class FakeThreatService:
    def __init__(
        self,
        threats,
    ):
        self.threats = threats

    def get_threats_for_profile(
        self,
        profile,
    ):
        return self.threats


class FakeRequirements:
    def __init__(
        self,
        mapping,
    ):
        self.mapping = mapping

    def get(
        self,
        threat_code,
    ):
        return self.mapping[
            threat_code
        ]


class FakeWeatherService:
    def __init__(
        self,
        weather=None,
        error=None,
    ):
        self.weather = weather
        self.error = error
        self.calls = 0

    def get_current_weather(
        self,
        location,
    ):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.weather


class FakeHistoricalWeatherService:
    def __init__(
        self,
        observations=(),
    ):
        self.observations = observations
        self.calls = 0

    def get_daily_temperatures(
        self,
        location,
        start_date,
        end_date,
    ):
        self.calls += 1

        return self.observations


@dataclass
class FakeContext:
    soil_temperature_10cm_estimate: (
        SoilTemperatureEstimate | None
    ) = None
    degree_days_10c: (
        DegreeDaysResult | None
    ) = None


class FakeEvaluator:
    def __init__(
        self,
        contexts,
    ):
        self.contexts = contexts
        self.calls = []

    def evaluate_with_context(
        self,
        threat_code,
        *,
        weather=None,
        historical_temperatures=None,
    ):
        self.calls.append(
            (
                threat_code,
                weather,
                historical_temperatures,
            )
        )

        result = RiskResult(
            threat_code=threat_code,
            status=RiskStatus.CALCULATED,
            risk_level=RiskLevel.HIGH,
            factors=(),
            explanation="Calculated.",
        )

        return (
            result,
            self.contexts[threat_code],
        )


def create_location():
    from app.domain import Location

    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_weather():
    return WeatherData(
        observed_at=datetime(
            2026,
            8,
            11,
            12,
            0,
        ),
        temperature=25.5,
        humidity=65.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )


def create_soil_estimate():
    return SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(
            6.0,
            18.0,
        ),
        source_temperatures=(
            16.0,
            10.0,
        ),
        method=(
            SoilTemperatureEstimateMethod
            .LINEAR_INTERPOLATION
        ),
    )


def create_observations():
    return (
        DailyTemperature(
            date=date(
                2026,
                5,
                1,
            ),
            mean_temperature=20.0,
        ),
        DailyTemperature(
            date=date(
                2026,
                5,
                2,
            ),
            mean_temperature=21.0,
        ),
    )


def create_degree_days(
    observations,
):
    return DegreeDaysResult(
        base_temperature=10.0,
        total=21.0,
        period_start=date(
            2026,
            5,
            1,
        ),
        period_end=date(
            2026,
            5,
            2,
        ),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod
            .DAILY_MEAN_ABOVE_BASE
        ),
    )


def create_threat(
    code,
    category,
):
    return Threat(
        code=code,
        name=code,
        category=category,
        description="Test threat.",
        active=True,
    )


def test_snapshot_captures_current_weather_and_soil_estimate():
    weather = create_weather()
    soil_estimate = create_soil_estimate()

    threat = create_threat(
        "COLORADO_BEETLE",
        "VEGETABLE_GARDEN",
    )

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=FakeThreatService(
            [threat]
        ),
        weather_service=FakeWeatherService(
            weather=weather
        ),
        historical_weather_service=(
            FakeHistoricalWeatherService()
        ),
        input_requirements=FakeRequirements(
            {
                "COLORADO_BEETLE": frozenset({
                    RiskInputCapability
                    .CURRENT_WEATHER,
                    RiskInputCapability
                    .SOIL_TEMPERATURE_10CM,
                }),
            }
        ),
        evaluator=FakeEvaluator(
            {
                "COLORADO_BEETLE": FakeContext(
                    soil_temperature_10cm_estimate=(
                        soil_estimate
                    ),
                ),
            }
        ),
    )

    (
        results,
        snapshot,
    ) = orchestrator.evaluate_with_snapshot(
        location=create_location(),
        profile=UserProfile.VEGETABLE_GARDEN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert len(results) == 1
    assert snapshot.current_weather is weather

    assert (
        snapshot
        .soil_temperature_10cm_estimate
        is soil_estimate
    )

    assert snapshot.degree_days_10c is None

    assert (
        snapshot.historical_observations
        is None
    )


def test_snapshot_captures_historical_inputs_and_degree_days():
    observations = create_observations()

    degree_days = create_degree_days(
        observations
    )

    threat = create_threat(
        "CODLING_MOTH",
        "GARDEN",
    )

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=FakeThreatService(
            [threat]
        ),
        weather_service=FakeWeatherService(),
        historical_weather_service=(
            FakeHistoricalWeatherService(
                observations=observations
            )
        ),
        input_requirements=FakeRequirements(
            {
                "CODLING_MOTH": frozenset({
                    RiskInputCapability
                    .DEGREE_DAYS_10C,
                }),
            }
        ),
        evaluator=FakeEvaluator(
            {
                "CODLING_MOTH": FakeContext(
                    degree_days_10c=(
                        degree_days
                    ),
                ),
            }
        ),
    )

    (
        results,
        snapshot,
    ) = orchestrator.evaluate_with_snapshot(
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

    assert (
        snapshot.historical_observations
        is observations
    )

    assert (
        snapshot.degree_days_10c
        is degree_days
    )

    assert snapshot.current_weather is None


def test_snapshot_does_not_invent_failed_weather_input():
    threat = create_threat(
        "TICK",
        "HUMAN",
    )

    evaluator = FakeEvaluator(
        {}
    )

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=FakeThreatService(
            [threat]
        ),
        weather_service=FakeWeatherService(
            error=WeatherTimeoutError(
                "Weather timeout."
            )
        ),
        historical_weather_service=(
            FakeHistoricalWeatherService()
        ),
        input_requirements=FakeRequirements(
            {
                "TICK": frozenset({
                    RiskInputCapability
                    .CURRENT_WEATHER,
                }),
            }
        ),
        evaluator=evaluator,
    )

    (
        results,
        snapshot,
    ) = orchestrator.evaluate_with_snapshot(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert len(results) == 1

    assert (
        results[0].status
        == RiskStatus.ERROR
    )

    assert snapshot.current_weather is None

    assert (
        snapshot
        .soil_temperature_10cm_estimate
        is None
    )

    assert snapshot.degree_days_10c is None

    assert (
        snapshot.historical_observations
        is None
    )

    assert evaluator.calls == []