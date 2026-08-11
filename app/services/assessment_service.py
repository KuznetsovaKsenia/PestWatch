from collections.abc import Callable
from datetime import date, datetime

from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    Location,
    RiskResult,
    UserProfile,
)
from app.repositories import AssessmentRepository


class AssessmentService:
    def __init__(
        self,
        repository: AssessmentRepository,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self._repository = repository
        self._clock = clock

    def save_assessment(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        input_snapshot: AssessmentInputSnapshot,
        risk_results: tuple[RiskResult, ...],
        historical_start_date: date | None = None,
    ) -> Assessment:
        assessment = Assessment(
            id=None,
            created_at=self._clock(),
            assessment_date=assessment_date,
            profile=profile,
            location=location,
            historical_start_date=(
                historical_start_date
            ),
            input_snapshot=input_snapshot,
            risk_results=risk_results,
        )

        return self._repository.save(
            assessment
        )