from datetime import date, datetime

from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    Location,
    UserProfile,
)
from app.domain.assessment_summary import AssessmentSummary
from app.services import AssessmentHistoryService


class FakeAssessmentRepository:
    def __init__(
        self,
        history=(),
        assessment=None,
    ):
        self.history = history
        self.assessment = assessment
        self.received_assessment_id = None

    def get_all(self):
        return self.history

    def get_by_id(
        self,
        assessment_id,
    ):
        self.received_assessment_id = (
            assessment_id
        )

        return self.assessment


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_summary():
    return AssessmentSummary(
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
    )


def create_assessment():
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
        historical_start_date=None,
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
        risk_results=(),
    )


def test_service_returns_history_from_repository():
    history = (
        create_summary(),
    )

    repository = FakeAssessmentRepository(
        history=history,
    )

    service = AssessmentHistoryService(
        repository
    )

    result = service.get_history()

    assert result is history


def test_service_returns_assessment_details():
    assessment = create_assessment()

    repository = FakeAssessmentRepository(
        assessment=assessment,
    )

    service = AssessmentHistoryService(
        repository
    )

    result = service.get_assessment(
        42
    )

    assert result is assessment
    assert (
        repository.received_assessment_id
        == 42
    )


def test_service_returns_none_for_unknown_assessment():
    repository = FakeAssessmentRepository(
        assessment=None,
    )

    service = AssessmentHistoryService(
        repository
    )

    result = service.get_assessment(
        999
    )

    assert result is None