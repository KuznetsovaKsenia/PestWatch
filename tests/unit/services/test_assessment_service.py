from datetime import date, datetime

from app.domain import (
    AssessmentInputSnapshot,
    Location,
    RiskLevel,
    RiskResult,
    RiskStatus,
    UserProfile,
)
from app.services import AssessmentService


class FakeAssessmentRepository:
    def __init__(self):
        self.received_assessment = None
        self.saved_assessment = None

    def save(self, assessment):
        self.received_assessment = assessment

        self.saved_assessment = type(
            assessment
        )(
            id=42,
            created_at=assessment.created_at,
            assessment_date=(
                assessment.assessment_date
            ),
            profile=assessment.profile,
            location=assessment.location,
            historical_start_date=(
                assessment.historical_start_date
            ),
            input_snapshot=(
                assessment.input_snapshot
            ),
            risk_results=(
                assessment.risk_results
            ),
        )

        return self.saved_assessment


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_result():
    return RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.HIGH,
        factors=(),
        explanation="Calculated.",
    )


def test_service_builds_assessment_from_supplied_data():
    repository = FakeAssessmentRepository()

    created_at = datetime(
        2026,
        8,
        11,
        16,
        0,
    )

    service = AssessmentService(
        repository=repository,
        clock=lambda: created_at,
    )

    location = create_location()
    snapshot = AssessmentInputSnapshot()

    results = (
        create_result(),
    )

    service.save_assessment(
        location=location,
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
        input_snapshot=snapshot,
        risk_results=results,
    )

    assessment = (
        repository.received_assessment
    )

    assert assessment.id is None
    assert assessment.created_at == created_at

    assert assessment.assessment_date == date(
        2026,
        8,
        11,
    )

    assert (
        assessment.profile
        == UserProfile.HUMAN
    )

    assert assessment.location is location

    assert assessment.historical_start_date is None

    assert assessment.input_snapshot is snapshot

    assert assessment.risk_results is results


def test_service_preserves_historical_start_date():
    repository = FakeAssessmentRepository()

    service = AssessmentService(
        repository=repository,
        clock=lambda: datetime(
            2026,
            8,
            11,
            16,
            0,
        ),
    )

    start_date = date(
        2026,
        5,
        1,
    )

    service.save_assessment(
        location=create_location(),
        profile=UserProfile.GARDEN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
        historical_start_date=start_date,
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
        risk_results=(
            create_result(),
        ),
    )

    assert (
        repository.received_assessment
        .historical_start_date
        == start_date
    )


def test_service_delegates_persistence_to_repository():
    repository = FakeAssessmentRepository()

    service = AssessmentService(
        repository=repository,
        clock=lambda: datetime(
            2026,
            8,
            11,
            16,
            0,
        ),
    )

    saved = service.save_assessment(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
        risk_results=(
            create_result(),
        ),
    )

    assert saved is repository.saved_assessment
    assert saved.id == 42


def test_service_does_not_modify_risk_results():
    repository = FakeAssessmentRepository()

    service = AssessmentService(
        repository=repository,
        clock=lambda: datetime(
            2026,
            8,
            11,
            16,
            0,
        ),
    )

    result = create_result()

    results = (
        result,
    )

    saved = service.save_assessment(
        location=create_location(),
        profile=UserProfile.HUMAN,
        assessment_date=date(
            2026,
            8,
            11,
        ),
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
        risk_results=results,
    )

    assert saved.risk_results is results
    assert saved.risk_results[0] is result