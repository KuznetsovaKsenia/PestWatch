from datetime import date, datetime

import pytest
from flask import Flask

from app.controllers.assessment_api import create_assessment_api
from app.domain.assessment_source import AssessmentSource
from app.domain.assessment_summary import AssessmentSummary
from app.domain.location import Location
from app.domain.user_profile import UserProfile


class FakeAssessmentHistoryService:
    def __init__(
        self,
        history=(),
    ):
        self.history = history

    def get_history(self):
        return self.history

    def get_assessment(
        self,
        assessment_id,
    ):
        return None


class UnusedAssessmentExecutionService:
    pass


class UnusedLocationService:
    pass


@pytest.fixture
def create_client():
    def factory(history=()):
        app = Flask(__name__)
        app.config["TESTING"] = True

        history_service = FakeAssessmentHistoryService(
            history=history,
        )

        app.register_blueprint(
            create_assessment_api(
                execution_service=(
                    UnusedAssessmentExecutionService()
                ),
                history_service=history_service,
                location_service=UnusedLocationService(),
            )
        )

        return app.test_client()

    return factory


def create_summary(
    *,
    assessment_id: int,
    created_at: datetime,
    assessment_date: date,
    profile: UserProfile,
    location_name: str,
    location_region: str,
    source: AssessmentSource,
) -> AssessmentSummary:
    return AssessmentSummary(
        id=assessment_id,
        created_at=created_at,
        assessment_date=assessment_date,
        profile=profile,
        location=Location(
            name=location_name,
            region=location_region,
            country="Россия",
            latitude=55.7558,
            longitude=37.6176,
        ),
        source=source,
    )


def test_get_assessments_returns_empty_history(
    create_client,
):
    client = create_client()

    response = client.get(
        "/api/assessments"
    )

    assert response.status_code == 200

    assert response.get_json() == {
        "success": True,
        "data": [],
    }


def test_get_assessments_returns_summary_contract(
    create_client,
):
    summary = create_summary(
        assessment_id=42,
        created_at=datetime(
            2026,
            8,
            12,
            20,
            31,
            14,
            482193,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=UserProfile.HUMAN,
        location_name="Москва",
        location_region="Москва",
        source=AssessmentSource.REAL,
    )

    client = create_client(
        history=(summary,),
    )

    response = client.get(
        "/api/assessments"
    )

    assert response.status_code == 200

    assert response.get_json() == {
        "success": True,
        "data": [
            {
                "id": 42,
                "created_at": (
                    "2026-08-12T20:31:14.482193"
                ),
                "assessment_date": (
                    "2026-08-12"
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


def test_get_assessments_does_not_expose_coordinates(
    create_client,
):
    summary = create_summary(
        assessment_id=1,
        created_at=datetime(
            2026,
            8,
            12,
            10,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=UserProfile.HUMAN,
        location_name="Москва",
        location_region="Москва",
        source=AssessmentSource.REAL,
    )

    client = create_client(
        history=(summary,),
    )

    response = client.get(
        "/api/assessments"
    )

    location = (
        response
        .get_json()["data"][0]["location"]
    )

    assert "latitude" not in location
    assert "longitude" not in location


def test_get_assessments_exposes_assessment_source(
    create_client,
):
    real = create_summary(
        assessment_id=2,
        created_at=datetime(
            2026,
            8,
            12,
            12,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=UserProfile.HUMAN,
        location_name="Москва",
        location_region="Москва",
        source=AssessmentSource.REAL,
    )

    demo = create_summary(
        assessment_id=1,
        created_at=datetime(
            2026,
            8,
            12,
            11,
            0,
        ),
        assessment_date=date(
            2026,
            5,
            13,
        ),
        profile=UserProfile.GARDEN,
        location_name="Тула",
        location_region="Тульская область",
        source=AssessmentSource.DEMO,
    )

    client = create_client(
        history=(
            real,
            demo,
        ),
    )

    response = client.get(
        "/api/assessments"
    )

    data = response.get_json()["data"]

    assert [
        item["source"]
        for item in data
    ] == [
        "REAL",
        "DEMO",
    ]


def test_get_assessments_preserves_history_order(
    create_client,
):
    newest = create_summary(
        assessment_id=3,
        created_at=datetime(
            2026,
            8,
            12,
            15,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=UserProfile.HUMAN,
        location_name="Москва",
        location_region="Москва",
        source=AssessmentSource.REAL,
    )

    older = create_summary(
        assessment_id=2,
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
        location_name="Казань",
        location_region=(
            "Республика Татарстан"
        ),
        source=AssessmentSource.REAL,
    )

    client = create_client(
        history=(
            newest,
            older,
        ),
    )

    response = client.get(
        "/api/assessments"
    )

    data = response.get_json()["data"]

    assert [
        item["id"]
        for item in data
    ] == [
        3,
        2,
    ]