from dataclasses import dataclass

from app.domain.recommendation import Recommendation
from app.domain.source import Source
from app.domain.threat import Threat


@dataclass(frozen=True)
class ThreatDetails:
    threat: Threat
    recommendations: tuple[Recommendation, ...]
    sources: tuple[Source, ...]