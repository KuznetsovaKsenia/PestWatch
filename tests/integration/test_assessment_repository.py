from datetime import date, datetime

import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    Location,
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskResult,
    RiskStatus,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    UserProfile,
    WeatherData,
)
from app.repositories import AssessmentRepository


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


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
        temperature=25.5,
        humidity=65.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
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


def create_factor():
    return RiskFactorResult(
        factor="SOIL_TEMPERATURE_10CM",
        state=RiskFactorState.MATCHED,
        actual_value=14.0,
        expected=">= 13 °C",
        explanation="Matched.",
        required=True,
    )


def create_assessment():
    observations = create_observations()

    return Assessment(
        id=None,
        created_at=datetime(
            2026,
            8,
            11,
            15,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.VEGETABLE_GARDEN,
        location=create_location(),
        historical_start_date=date(
            2026,
            5,
            1,
        ),
        input_snapshot=AssessmentInputSnapshot(
            current_weather=create_weather(),
            soil_temperature_10cm_estimate=(
                create_soil_estimate()
            ),
            degree_days_10c=create_degree_days(
                observations
            ),
            historical_observations=observations,
        ),
        risk_results=(
            RiskResult(
                threat_code="COLORADO_BEETLE",
                status=RiskStatus.CALCULATED,
                risk_level=RiskLevel.HIGH,
                factors=(
                    create_factor(),
                ),
                explanation="Calculated.",
            ),
        ),
    )


def test_repository_saves_assessment(app):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        assert saved.id is not None


def test_repository_restores_assessment_metadata(app):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        assert restored is not None
        assert restored.id == saved.id

        assert restored.created_at == datetime(
            2026,
            8,
            11,
            15,
            0,
        )

        assert restored.assessment_date == date(
            2026,
            8,
            11,
        )

        assert (
            restored.profile
            == UserProfile.VEGETABLE_GARDEN
        )

        assert restored.location == create_location()

        assert (
            restored.historical_start_date
            == date(
                2026,
                5,
                1,
            )
        )


def test_repository_restores_current_weather_snapshot(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        weather = (
            restored.input_snapshot
            .current_weather
        )

        assert weather is not None

        assert weather.observed_at == datetime(
            2026,
            8,
            11,
            12,
            0,
        )

        assert weather.temperature == pytest.approx(
            25.5
        )

        assert weather.humidity == pytest.approx(
            65.0
        )

        assert (
            weather.soil_temperature_6cm
            == pytest.approx(16.0)
        )

        assert (
            weather.soil_temperature_18cm
            == pytest.approx(10.0)
        )


def test_repository_restores_soil_temperature_estimate(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        estimate = (
            restored.input_snapshot
            .soil_temperature_10cm_estimate
        )

        assert estimate is not None
        assert estimate.depth_cm == 10.0

        assert estimate.temperature == pytest.approx(
            14.0
        )

        assert estimate.source_depths_cm == (
            6.0,
            18.0,
        )

        assert estimate.source_temperatures == (
            16.0,
            10.0,
        )

        assert (
            estimate.method
            == SoilTemperatureEstimateMethod
            .LINEAR_INTERPOLATION
        )


def test_repository_restores_degree_days_snapshot(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        degree_days = (
            restored.input_snapshot
            .degree_days_10c
        )

        assert degree_days is not None

        assert (
            degree_days.base_temperature
            == pytest.approx(10.0)
        )

        assert degree_days.total == pytest.approx(
            21.0
        )

        assert degree_days.period_start == date(
            2026,
            5,
            1,
        )

        assert degree_days.period_end == date(
            2026,
            5,
            2,
        )

        assert (
            degree_days.method
            == DegreeDaysCalculationMethod
            .DAILY_MEAN_ABOVE_BASE
        )


def test_repository_restores_historical_observations(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        observations = (
            restored.input_snapshot
            .historical_observations
        )

        assert observations == create_observations()

        assert (
            restored.input_snapshot
            .degree_days_10c
            .observations
            == observations
        )


def test_repository_restores_risk_results_and_factors(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        saved = repository.save(
            create_assessment()
        )

        restored = repository.get_by_id(
            saved.id
        )

        assert len(restored.risk_results) == 1

        result = restored.risk_results[0]

        assert (
            result.threat_code
            == "COLORADO_BEETLE"
        )

        assert (
            result.status
            == RiskStatus.CALCULATED
        )

        assert result.risk_level == RiskLevel.HIGH
        assert result.explanation == "Calculated."

        assert len(result.factors) == 1

        factor = result.factors[0]

        assert (
            factor.factor
            == "SOIL_TEMPERATURE_10CM"
        )

        assert (
            factor.state
            == RiskFactorState.MATCHED
        )

        assert factor.actual_value == pytest.approx(
            14.0
        )

        assert factor.expected == ">= 13 °C"
        assert factor.explanation == "Matched."
        assert factor.required is True


def test_repository_restores_error_result(app):
    with app.app_context():
        assessment = create_assessment()

        assessment = Assessment(
            id=assessment.id,
            created_at=assessment.created_at,
            assessment_date=(
                assessment.assessment_date
            ),
            profile=assessment.profile,
            location=assessment.location,
            historical_start_date=(
                assessment.historical_start_date
            ),
            input_snapshot=assessment.input_snapshot,
            risk_results=(
                RiskResult(
                    threat_code="COLORADO_BEETLE",
                    status=RiskStatus.ERROR,
                    risk_level=None,
                    factors=(),
                    explanation="Weather timeout.",
                ),
            ),
        )

        repository = AssessmentRepository()

        saved = repository.save(
            assessment
        )

        restored = repository.get_by_id(
            saved.id
        )

        result = restored.risk_results[0]

        assert result.status == RiskStatus.ERROR
        assert result.risk_level is None
        assert result.factors == ()

        assert (
            result.explanation
            == "Weather timeout."
        )


def test_repository_returns_none_for_unknown_id(
    app,
):
    with app.app_context():
        repository = AssessmentRepository()

        result = repository.get_by_id(
            999999
        )

        assert result is None