from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskStatus,
)


class RiskPolicy:
    def determine_status(
        self,
        factors: tuple[RiskFactorResult, ...],
    ) -> RiskStatus:
        if not factors:
            return RiskStatus.INSUFFICIENT_DATA

        if any(
            factor.required
            and factor.state == RiskFactorState.MISSING
            for factor in factors
        ):
            return RiskStatus.INSUFFICIENT_DATA

        if any(
            not factor.required
            and factor.state == RiskFactorState.MISSING
            for factor in factors
        ):
            return RiskStatus.LIMITED

        return RiskStatus.CALCULATED

    def determine_level(
        self,
        factors: tuple[RiskFactorResult, ...],
        status: RiskStatus,
    ) -> RiskLevel | None:
        if status in {
            RiskStatus.INSUFFICIENT_DATA,
            RiskStatus.ERROR,
        }:
            return None

        known_factors = tuple(
            factor
            for factor in factors
            if factor.state != RiskFactorState.MISSING
        )

        if not known_factors:
            return None

        matched_count = sum(
            factor.state == RiskFactorState.MATCHED
            for factor in known_factors
        )

        match_ratio = matched_count / len(known_factors)

        return self._level_from_ratio(match_ratio)

    @staticmethod
    def _level_from_ratio(
        match_ratio: float,
    ) -> RiskLevel:
        if match_ratio < 0.25:
            return RiskLevel.LOW

        if match_ratio < 0.50:
            return RiskLevel.MODERATE

        if match_ratio < 0.75:
            return RiskLevel.ELEVATED

        return RiskLevel.HIGH