from datetime import date, datetime

import pytest
from flask import Flask

from app.controllers.assessment_api import (
    create_assessment_api,
)
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
from app.domain.assessment_summary import AssessmentSummary
from app.integrations.geocoding import GeocodingTimeoutError
from app.services import LocationNotFoundError


class FakeExecutionService:
    def __init__(
        self,
        assessment=None,
        error=None,
    ):
        self.assessment = assessment
        self.error = error
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)

        if self.error is not None:
            raise self.error

        return self.assessment


class FakeLocationService:
    def __init__(
        self,
        location=None,
        error=None,
    ):
        self.location = location or create_location()
        self.error = error
        self.calls = []

    def resolve(self, **kwargs):
        self.calls.append(kwargs)

        if self.error is not None:
            raise self.error

        return self.location


class FakeHistoryService:
    def __init__(
        self,
        history=(),
        assessment=None,
    ):
        self.history = history
        self.assessment = assessment
        self.received_assessment_id = None

    def get_history(self):
        return self.history

    def get_assessment(
        self,
        assessment_id,
    ):
        self.received_assessment_id = assessment_id
        return self.assessment


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_assessment():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
    )

    weather = WeatherData(
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

    soil_estimate = SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(6.0, 18.0),
        source_temperatures=(16.0, 10.0),
        method=(
            SoilTemperatureEstimateMethod
            .LINEAR_INTERPOLATION
        ),
    )

    degree_days = DegreeDaysResult(
        base_temperature=10.0,
        total=10.0,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 1),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod
            .DAILY_MEAN_ABOVE_BASE
        ),
    )

    factor = RiskFactorResult(
        factor="AIR_TEMPERATURE",
        state=RiskFactorState.MATCHED,
        actual_value=25.5,
        expected=">= 10 °C",
        explanation="Matched.",
        required=True,
    )

    result = RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.HIGH,
        factors=(factor,),
        explanation="Calculated.",
    )

    return Assessment(
        id=42,
        created_at=datetime(
            2026,
            8,
            11,
            16,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.HUMAN,
        location=create_location(),
        historical_start_date=date(
            2026,
            5,
            1,
        ),
        input_snapshot=(
            AssessmentInputSnapshot(
                current_weather=weather,
                soil_temperature_10cm_estimate=(
                    soil_estimate
                ),
                degree_days_10c=degree_days,
                saturation_deficit_mm_hg=1.25,
                historical_observations=(
                    observations
                ),
            )
        ),
        risk_results=(result,),
    )


def create_summary():
    assessment = create_assessment()

    return AssessmentSummary(
        id=assessment.id,
        created_at=assessment.created_at,
        assessment_date=(
            assessment.assessment_date
        ),
        profile=assessment.profile,
        location=assessment.location,
    )


@pytest.fixture
def api_client():
    def factory(
        *,
        execution_service=None,
        history_service=None,
        location_service=None,
    ):
        app = Flask(__name__)
        app.config["TESTING"] = True

        app.register_blueprint(
            create_assessment_api(
                execution_service=(
                    execution_service
                    or FakeExecutionService()
                ),
                history_service=(
                    history_service
                    or FakeHistoryService()
                ),
                location_service=(
                    location_service
                    or FakeLocationService()
                ),
                assessment_date_provider=(
                    lambda: date(2026, 8, 11)
                ),
            )
        )

        return app.test_client()

    return factory


def test_post_assessment_executes_and_returns_persisted_assessment(
    api_client,
):
    assessment = create_assessment()
    execution_service = FakeExecutionService(
        assessment=assessment
    )
    location_service = FakeLocationService()
    client = api_client(
        execution_service=execution_service,
        location_service=location_service,
    )

    response = client.post(
        "/api/assessments",
        json={
            "location": {
                "name": "Москва",
                "region": "Москва",
                "country": "Россия",
            },
            "profile": "HUMAN",
        },
    )
    body = response.get_json()

    assert response.status_code == 201
    assert body["success"] is True
    assert body["data"]["id"] == 42
    assert body["data"]["profile"] == "HUMAN"

    assert (
        body["data"]["input_snapshot"]
        ["current_weather"]["humidity"]
        == 65.0
    )

    assert (
        body["data"]["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
        ["source_depths_cm"]
        == [6.0, 18.0]
    )

    assert (
        body["data"]["input_snapshot"]
        ["saturation_deficit_mm_hg"]
        == pytest.approx(1.25)
    )

    assert (
        body["data"]["risk_results"][0]
        ["status"]
        == "CALCULATED"
    )

    assert location_service.calls == [
        {
            "name": "Москва",
            "region": "Москва",
            "country": "Россия",
        }
    ]

    call = execution_service.calls[0]

    assert call["location"] == create_location()
    assert call["profile"] == UserProfile.HUMAN

    assert call["assessment_date"] == date(
        2026,
        8,
        11,
    )

    assert "historical_start_date" not in call


def test_post_assessment_rejects_invalid_request(
    api_client,
):
    client = api_client()

    response = client.post(
        "/api/assessments",
        json={
            "profile": "UNKNOWN",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "INVALID_REQUEST",
            "message": (
                "Request contains invalid "
                "assessment input."
            ),
        },
    }


def test_post_assessment_rejects_missing_location_region_before_execution(
    api_client,
):
    execution_service = FakeExecutionService()
    client = api_client(
        execution_service=execution_service
    )

    response = client.post(
        "/api/assessments",
        json={
            "location": {
                "name": "Москва",
                "country": "Россия",
            },
            "profile": "HUMAN",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "INVALID_REQUEST",
            "message": (
                "Request contains invalid "
                "assessment input."
            ),
        },
    }
    assert execution_service.calls == []


def test_get_assessments_returns_history_summaries(
    api_client,
):
    history_service = FakeHistoryService(
        history=(create_summary(),)
    )

    client = api_client(
        history_service=history_service
    )

    response = client.get(
        "/api/assessments"
    )

    body = response.get_json()

    assert response.status_code == 200

    assert body == {
    "success": True,
    "data": [
        {
            "id": 42,
            "created_at": (
                "2026-08-11T16:00:00"
            ),
            "assessment_date": (
                "2026-08-11"
            ),
            "profile": "HUMAN",
            "location": {
                "name": "Москва",
                "region": "Москва",
                "country": "Россия",
            },
            "source": "REAL",
        }
    ],
}


def test_get_assessment_returns_stored_full_assessment(
    api_client,
):
    assessment = create_assessment()

    history_service = FakeHistoryService(
        assessment=assessment
    )

    client = api_client(
        history_service=history_service
    )

    response = client.get(
        "/api/assessments/42"
    )

    body = response.get_json()

    assert response.status_code == 200

    assert body == {
        "success": True,
        "data": {
            "id": 42,
            "created_at": (
                "2026-08-11T16:00:00"
            ),
            "assessment_date": (
                "2026-08-11"
            ),
            "profile": "HUMAN",
            "location": {
                "name": "Москва",
                "region": "Москва",
                "country": "Россия",
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
            "source": "REAL",
            "historical_start_date": (
                "2026-05-01"
            ),
            "input_snapshot": {
                "current_weather": {
                    "observed_at": (
                        "2026-08-11T12:00:00"
                    ),
                    "temperature": 25.5,
                    "humidity": 65.0,
                    "precipitation": 0.0,
                    "wind_speed": 2.0,
                    "soil_temperature": 18.0,
                    "soil_temperature_6cm": 16.0,
                    "soil_temperature_18cm": 10.0,
                },
                "soil_temperature_10cm_estimate": {
                    "depth_cm": 10.0,
                    "temperature": 14.0,
                    "source_depths_cm": [
                        6.0,
                        18.0,
                    ],
                    "source_temperatures": [
                        16.0,
                        10.0,
                    ],
                    "method": (
                        "LINEAR_INTERPOLATION"
                    ),
                },
                "degree_days_10c": {
                    "base_temperature": 10.0,
                    "total": 10.0,
                    "period_start": (
                        "2026-05-01"
                    ),
                    "period_end": (
                        "2026-05-01"
                    ),
                    "observations": [
                        {
                            "date": (
                                "2026-05-01"
                            ),
                            "mean_temperature": 20.0,
                        }
                    ],
                    "method": (
                        "DAILY_MEAN_ABOVE_BASE"
                    ),
                },
                "saturation_deficit_mm_hg": 1.25,
                "historical_observations": [
                    {
                        "date": (
                            "2026-05-01"
                        ),
                        "mean_temperature": 20.0,
                    }
                ],
            },
            "risk_results": [
                {
                    "threat_code": "TICK",
                    "status": "CALCULATED",
                    "risk_level": "HIGH",
                    "factors": [
                        {
                            "factor": (
                                "AIR_TEMPERATURE"
                            ),
                            "state": "MATCHED",
                            "actual_value": 25.5,
                            "expected": ">= 10 °C",
                            "explanation": (
                                "Matched."
                            ),
                            "required": True,
                        }
                    ],
                    "explanation": (
                        "Calculated."
                    ),
                }
            ],
        },
    }

    assert (
        history_service.received_assessment_id
        == 42
    )

def test_get_unknown_assessment_returns_404(
    api_client,
):
    client = api_client(
        history_service=(
            FakeHistoryService(
                assessment=None
            )
        )
    )

    response = client.get(
        "/api/assessments/999"
    )

    assert response.status_code == 404

    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "ASSESSMENT_NOT_FOUND",
            "message": "Assessment not found.",
        },
    }

def test_post_assessment_returns_400_when_location_not_found(
    api_client,
):
    execution_service = FakeExecutionService()
    location_service = FakeLocationService(
        error=LocationNotFoundError(
            "Location not found."
        )
    )
    client = api_client(
        execution_service=execution_service,
        location_service=location_service,
    )

    response = client.post(
        "/api/assessments",
        json={
            "location": {
                "name": "Несуществующий город",
                "region": "Москва",
                "country": "Россия",
            },
            "profile": "HUMAN",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == (
        "LOCATION_NOT_FOUND"
    )
    assert execution_service.calls == []


def test_post_assessment_returns_503_when_geocoding_is_unavailable(
    api_client,
):
    execution_service = FakeExecutionService()
    location_service = FakeLocationService(
        error=GeocodingTimeoutError(
            "Provider timeout."
        )
    )
    client = api_client(
        execution_service=execution_service,
        location_service=location_service,
    )

    response = client.post(
        "/api/assessments",
        json={
            "location": {
                "name": "Москва",
                "region": "Москва",
                "country": "Россия",
            },
            "profile": "HUMAN",
        },
    )

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == (
        "LOCATION_SERVICE_UNAVAILABLE"
    )
    assert execution_service.calls == []
