from app.domain import (
    RiskFactorResult,
    RiskResult,
    RiskStatus,
)
from app.risk.policy import RiskPolicy


class RiskEngine:
    def __init__(
        self,
        policy: RiskPolicy,
    ):
        self._policy = policy

    def evaluate(
        self,
        threat_code: str,
        factors: tuple[RiskFactorResult, ...],
    ) -> RiskResult:
        status = self._policy.determine_status(factors)
        risk_level = self._policy.determine_level(
            factors,
            status,
        )

        return RiskResult(
            threat_code=threat_code,
            status=status,
            risk_level=risk_level,
            factors=factors,
            explanation=self._build_explanation(status),
        )

    @staticmethod
    def _build_explanation(
        status: RiskStatus,
    ) -> str:
        if status == RiskStatus.CALCULATED:
            return (
                "Оценка выполнена по всем доступным факторам."
            )

        if status == RiskStatus.LIMITED:
            return (
                "Оценка выполнена по обязательным факторам, "
                "часть дополнительных данных отсутствует."
            )

        if status == RiskStatus.INSUFFICIENT_DATA:
            return (
                "Недостаточно обязательных данных для оценки."
            )

        return "Не удалось выполнить оценку риска."