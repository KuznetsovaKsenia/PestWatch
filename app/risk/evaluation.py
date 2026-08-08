from dataclasses import dataclass

from app.domain import RiskFactorResult


@dataclass(frozen=True)
class RiskEvaluation:
    threat_code: str
    factors: tuple[RiskFactorResult, ...]