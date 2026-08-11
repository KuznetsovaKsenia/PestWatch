from app.risk.calculator import RiskCalculator


class RiskCalculatorNotFoundError(LookupError):
    pass


class RiskCalculatorRegistry:
    def __init__(
        self,
        calculators: dict[str, RiskCalculator],
    ):
        self._calculators = dict(calculators)

    def get(
        self,
        threat_code: str,
    ) -> RiskCalculator:
        try:
            return self._calculators[threat_code]
        except KeyError as exc:
            raise RiskCalculatorNotFoundError(
                f"No risk calculator registered for threat: {threat_code}"
            ) from exc