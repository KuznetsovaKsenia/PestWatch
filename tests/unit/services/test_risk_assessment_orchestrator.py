from datetime import date, datetime

import pytest

from app.domain import (
    DailyTemperature,
    Location,
    RiskInputCapability,
    RiskLevel,
    RiskResult,
    RiskStatus,
    Threat,
    UserProfile,
    WeatherData,
)
from app.integrations.weather import (
    WeatherConnectionError,
    WeatherTimeoutError,
)
from app.risk import RiskInputUnavailableError
from app.services import (
    HistoricalPeriodRequiredError,
    RiskAssessmentOrchestrator,
)


class FakeThreatService:
    def __init__(self, threats):
        self.threats = threats
        self.received_profile = None

    def get_threats_for_profile(self, profile):
        self.received_profile = profile
        return self.threats


class FakeRiskInputRequirements:
    def __init__(self, requirements):
        self.requirements = requirements
        self.received_threat_codes = []

    def get(self, threat_code):
        self.received_threat_codes.append(
            threat_code
        )
        return self.requirements[threat_code]


class FakeWeatherService:
    def __init__(
        self,
        weather,
        error=None,
    ):
        self.weather = weather
        self.error = error
        self.calls = 0
        self.received_location = None

    def get_current_weather(self, location):
        self.calls += 1
        self.received_location = location

        if self.error is not None:
            raise self.error

        return self.weather


class FakeHistoricalWeatherService:
    def __init__(
        self,
        observations,
        error=None,
    ):
        self.observations = observations
        self.error = error
        self.calls = 0
        self.received_location = None
        self.received_start_date = None
        self.received_end_date = None

    def get_daily_temperatures(
        self,
        location,
        start_date,
        end_date,
    ):
        self.calls += 1
        self.received_location = location
        self.received_start_date = start_date
        self.received_end_date = end_date

        if self.error is not None:
            raise self.error

        return self.observations


class FakeSingleThreatRiskEvaluator:
    def __init__(
        self,
        errors=None,
    ):
        self.calls = []
        self.errors = errors or {}

    def evaluate(
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

        if threat_code in self.errors:
            raise self.errors[threat_code]

        return RiskResult(
            threat_code=threat_code,
            status=RiskStatus.CALCULATED,
            risk_level=RiskLevel.HIGH,
            factors=(),
            explanation="Calculated.",
        )


def create_location():
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
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
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


def create_orchestrator(
    *,
    threats,
    requirements,
    weather=None,
    observations=(),
    weather_error=None,
    historical_error=None,
    evaluator_errors=None,
):
    threat_service = FakeThreatService(
        threats
    )

    input_requirements = (
        FakeRiskInputRequirements(
            requirements
        )
    )

    weather_service = FakeWeatherService(
        weather,
        error=weather_error,
    )

    historical_weather_service = (
        FakeHistoricalWeatherService(
            observations,
            error=historical_error,
        )
    )

    evaluator = FakeSingleThreatRiskEvaluator(
        errors=evaluator_errors,
    )

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=threat_service,
        weather_service=weather_service,
        historical_weather_service=(
            historical_weather_service
        ),
        input_requirements=input_requirements,
        evaluator=evaluator,
    )

    return (
        orchestrator,
        threat_service,
        weather_service,
        historical_weather_service,
        evaluator,
    )


def test_orchestrator_selects_threats_by_profile():
    threat = create_threat(
        "TICK",
        "HUMAN",
    )

    (
        orchestrator,
        threat_service,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=[threat],
        requirements={
            "TICK": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather=create_weather(),
    )

    orchestrator.evaluate(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert (
        threat_service.received_profile
        == UserProfile.HUMAN
    )


def test_current_weather_is_acquired_once_for_multiple_threats():
    weather = create_weather()

    threats = [
        create_threat(
            "COLORADO_BEETLE",
            "VEGETABLE_GARDEN",
        ),
        create_threat(
            "CABBAGE_APHID",
            "VEGETABLE_GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        weather_service,
        _,
        _,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "COLORADO_BEETLE": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
            "CABBAGE_APHID": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather=weather,
    )

    orchestrator.evaluate(
        location=create_location(),
        profile=(
            UserProfile.VEGETABLE_GARDEN
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert weather_service.calls == 1


def test_historical_weather_is_not_requested_when_not_required():
    (
        orchestrator,
        _,
        _,
        historical_weather_service,
        _,
    ) = create_orchestrator(
        threats=[
            create_threat(
                "TICK",
                "HUMAN",
            ),
        ],
        requirements={
            "TICK": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather=create_weather(),
    )

    orchestrator.evaluate(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert (
        historical_weather_service.calls
        == 0
    )


def test_historical_weather_uses_requested_period():
    observations = (
        DailyTemperature(
            date=date(
                2026,
                5,
                1,
            ),
            mean_temperature=20.0,
        ),
    )

    (
        orchestrator,
        _,
        weather_service,
        historical_weather_service,
        _,
    ) = create_orchestrator(
        threats=[
            create_threat(
                "CODLING_MOTH",
                "GARDEN",
            ),
        ],
        requirements={
            "CODLING_MOTH": frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        },
        observations=observations,
    )

    orchestrator.evaluate(
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

    assert weather_service.calls == 0

    assert (
        historical_weather_service.calls
        == 1
    )

    assert (
        historical_weather_service
        .received_start_date
        == date(
            2026,
            5,
            1,
        )
    )

    assert (
        historical_weather_service
        .received_end_date
        == date(
            2026,
            8,
            11,
        )
    )


def test_each_threat_receives_only_required_inputs():
    weather = create_weather()

    observations = (
        DailyTemperature(
            date=date(
                2026,
                5,
                1,
            ),
            mean_temperature=20.0,
        ),
    )

    threats = [
        create_threat(
            "TICK",
            "HUMAN",
        ),
        create_threat(
            "CODLING_MOTH",
            "GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        _,
        _,
        evaluator,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "TICK": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
            "CODLING_MOTH": frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        },
        weather=weather,
        observations=observations,
    )

    orchestrator.evaluate(
        location=create_location(),
        profile=UserProfile.HUMAN,
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

    assert evaluator.calls == [
        (
            "TICK",
            weather,
            None,
        ),
        (
            "CODLING_MOTH",
            None,
            observations,
        ),
    ]


def test_results_preserve_threat_order():
    threats = [
        create_threat(
            "COLORADO_BEETLE",
            "VEGETABLE_GARDEN",
        ),
        create_threat(
            "CABBAGE_APHID",
            "VEGETABLE_GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "COLORADO_BEETLE": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
            "CABBAGE_APHID": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather=create_weather(),
    )

    results = orchestrator.evaluate(
        location=create_location(),
        profile=(
            UserProfile.VEGETABLE_GARDEN
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert tuple(
        result.threat_code
        for result in results
    ) == (
        "COLORADO_BEETLE",
        "CABBAGE_APHID",
    )


def test_historical_period_is_required_when_needed():
    (
        orchestrator,
        _,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=[
            create_threat(
                "CODLING_MOTH",
                "GARDEN",
            ),
        ],
        requirements={
            "CODLING_MOTH": frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        },
    )

    with pytest.raises(
        HistoricalPeriodRequiredError,
        match=(
            "Historical start date is required"
        ),
    ):
        orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.GARDEN,
            assessment_date=date(
                2026,
                8,
                11,
            ),
        )


def test_historical_start_date_cannot_be_after_assessment_date():
    (
        orchestrator,
        _,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=[
            create_threat(
                "CODLING_MOTH",
                "GARDEN",
            ),
        ],
        requirements={
            "CODLING_MOTH": frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        },
    )

    with pytest.raises(
        HistoricalPeriodRequiredError,
        match=(
            "Historical start date cannot be "
            "after assessment date"
        ),
    ):
        orchestrator.evaluate(
            location=create_location(),
            profile=UserProfile.GARDEN,
            assessment_date=date(
                2026,
                5,
                1,
            ),
            historical_start_date=date(
                2026,
                8,
                11,
            ),
        )


def test_current_weather_failure_returns_error_for_dependent_threats():
    threats = [
        create_threat(
            "COLORADO_BEETLE",
            "VEGETABLE_GARDEN",
        ),
        create_threat(
            "CABBAGE_APHID",
            "VEGETABLE_GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        _,
        _,
        evaluator,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "COLORADO_BEETLE": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
            "CABBAGE_APHID": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather_error=WeatherTimeoutError(
            "Weather timeout."
        ),
    )

    results = orchestrator.evaluate(
        location=create_location(),
        profile=(
            UserProfile.VEGETABLE_GARDEN
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert tuple(
        result.status
        for result in results
    ) == (
        RiskStatus.ERROR,
        RiskStatus.ERROR,
    )

    assert all(
        result.risk_level is None
        for result in results
    )

    assert evaluator.calls == []


def test_historical_failure_does_not_break_current_weather_threat():
    weather = create_weather()

    threats = [
        create_threat(
            "TICK",
            "HUMAN",
        ),
        create_threat(
            "CODLING_MOTH",
            "GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        _,
        _,
        evaluator,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "TICK": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
            "CODLING_MOTH": frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        },
        weather=weather,
        historical_error=(
            WeatherConnectionError(
                "Archive unavailable."
            )
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
        historical_start_date=date(
            2026,
            5,
            1,
        ),
    )

    assert results[0].threat_code == "TICK"
    assert (
        results[0].status
        == RiskStatus.CALCULATED
    )

    assert (
        results[1].threat_code
        == "CODLING_MOTH"
    )
    assert (
        results[1].status
        == RiskStatus.ERROR
    )
    assert results[1].risk_level is None

    assert evaluator.calls == [
        (
            "TICK",
            weather,
            None,
        ),
    ]


def test_preparation_failure_is_isolated_to_single_threat():
    weather = create_weather()

    threats = [
        create_threat(
            "COLORADO_BEETLE",
            "VEGETABLE_GARDEN",
        ),
        create_threat(
            "CABBAGE_APHID",
            "VEGETABLE_GARDEN",
        ),
    ]

    (
        orchestrator,
        _,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=threats,
        requirements={
            "COLORADO_BEETLE": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
            "CABBAGE_APHID": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather=weather,
        evaluator_errors={
            "COLORADO_BEETLE": (
                RiskInputUnavailableError(
                    "Soil temperature input "
                    "is unavailable."
                )
            ),
        },
    )

    results = orchestrator.evaluate(
        location=create_location(),
        profile=(
            UserProfile.VEGETABLE_GARDEN
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )

    assert (
        results[0].threat_code
        == "COLORADO_BEETLE"
    )
    assert (
        results[0].status
        == RiskStatus.ERROR
    )
    assert results[0].risk_level is None

    assert (
        results[1].threat_code
        == "CABBAGE_APHID"
    )
    assert (
        results[1].status
        == RiskStatus.CALCULATED
    )


def test_error_result_contains_technical_explanation():
    (
        orchestrator,
        _,
        _,
        _,
        _,
    ) = create_orchestrator(
        threats=[
            create_threat(
                "TICK",
                "HUMAN",
            ),
        ],
        requirements={
            "TICK": frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        },
        weather_error=WeatherTimeoutError(
            "Weather timeout."
        ),
    )

    result = orchestrator.evaluate(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
    )[0]

    assert result.status == RiskStatus.ERROR
    assert result.risk_level is None
    assert result.factors == ()
    assert (
        result.explanation
        == "Weather timeout."
    )