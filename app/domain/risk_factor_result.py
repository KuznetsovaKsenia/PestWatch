from dataclasses import dataclass

from app.domain.risk_factor_state import RiskFactorState


@dataclass(frozen=True)
class RiskFactorResult:
    factor: str
    state: RiskFactorState
    actual_value: object | None
    expected: str | None
    explanation: str