from datetime import date

from app.domain import (
    Assessment,
    Location,
    UserProfile,
)
from app.services.assessment_service import (
    AssessmentService,
)
from app.services.risk_assessment_orchestrator import (
    RiskAssessmentOrchestrator,
)


class AssessmentExecutionService:
    def __init__(
        self,
        orchestrator: RiskAssessmentOrchestrator,
        assessment_service: AssessmentService,
    ):
        self._orchestrator = orchestrator
        self._assessment_service = (
            assessment_service
        )

    def execute(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> Assessment:
        (
            risk_results,
            input_snapshot,
        ) = (
            self._orchestrator
            .evaluate_with_snapshot(
                location=location,
                profile=profile,
                assessment_date=assessment_date,
                historical_start_date=(
                    historical_start_date
                ),
            )
        )

        return (
            self._assessment_service
            .save_assessment(
                location=location,
                profile=profile,
                assessment_date=assessment_date,
                historical_start_date=(
                    historical_start_date
                ),
                input_snapshot=input_snapshot,
                risk_results=risk_results,
            )
        )