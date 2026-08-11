from dataclasses import dataclass
from datetime import date, datetime

from app.domain.location import Location
from app.domain.risk_result import RiskResult
from app.domain.user_profile import UserProfile
from app.domain.assessment_input_snapshot import (
    AssessmentInputSnapshot,
)


@dataclass(frozen=True)
class Assessment:
    id: int | None
    created_at: datetime
    assessment_date: date
    profile: UserProfile
    location: Location
    historical_start_date: date | None
    risk_results: tuple[RiskResult, ...]
    input_snapshot: AssessmentInputSnapshot

    def __post_init__(self):
        if (
            self.historical_start_date is not None
            and self.historical_start_date
            > self.assessment_date
        ):
            raise ValueError(
                "Historical start date cannot be "
                "after assessment date."
            )