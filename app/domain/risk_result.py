from dataclasses import dataclass

from app.domain.risk_factor_result import RiskFactorResult
from app.domain.risk_level import RiskLevel
from app.domain.risk_status import RiskStatus


@dataclass(frozen=True)
class RiskResult:
    threat_code: str
    status: RiskStatus
    risk_level: RiskLevel | None
    factors: tuple[RiskFactorResult, ...]
    explanation: str

    def __post_init__(self):
        if self.status == RiskStatus.CALCULATED and self.risk_level is None:
            raise ValueError(
                "RiskLevel is required when status is CALCULATED."
            )