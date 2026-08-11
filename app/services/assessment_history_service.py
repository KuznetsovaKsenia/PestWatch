from app.domain import Assessment
from app.domain.assessment_summary import AssessmentSummary
from app.repositories import AssessmentRepository


class AssessmentHistoryService:
    def __init__(
        self,
        repository: AssessmentRepository,
    ):
        self._repository = repository

    def get_history(
        self,
    ) -> tuple[AssessmentSummary, ...]:
        return self._repository.get_all()

    def get_assessment(
        self,
        assessment_id: int,
    ) -> Assessment | None:
        return self._repository.get_by_id(
            assessment_id
        )