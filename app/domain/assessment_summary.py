from dataclasses import dataclass
from datetime import date, datetime

from app.domain.assessment_source import AssessmentSource
from app.domain.location import Location
from app.domain.user_profile import UserProfile


@dataclass(frozen=True)
class AssessmentSummary:
    id: int
    created_at: datetime
    assessment_date: date
    profile: UserProfile
    location: Location
    source: AssessmentSource = AssessmentSource.REAL