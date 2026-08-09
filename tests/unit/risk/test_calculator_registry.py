import pytest

from app.domain import RiskContext, RiskFactorResult
from app.risk import (
    RiskCalculator,
    RiskCalculatorNotFoundError,
    RiskCalculatorRegistry,
)


class FakeRiskCalculator(RiskCalculator):
    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        return ()


def test_registry_returns_registered_calculator():
    calculator = FakeRiskCalculator()

    registry = RiskCalculatorRegistry(
        calculators={
            "TICK": calculator,
        },
    )

    result = registry.get("TICK")

    assert result is calculator


def test_registry_returns_correct_calculator_for_code():
    tick_calculator = FakeRiskCalculator()
    aphid_calculator = FakeRiskCalculator()

    registry = RiskCalculatorRegistry(
        calculators={
            "TICK": tick_calculator,
            "CABBAGE_APHID": aphid_calculator,
        },
    )

    assert registry.get("TICK") is tick_calculator
    assert registry.get("CABBAGE_APHID") is aphid_calculator


def test_registry_raises_for_unknown_threat_code():
    registry = RiskCalculatorRegistry(
        calculators={},
    )

    with pytest.raises(
        RiskCalculatorNotFoundError,
        match="No risk calculator registered for threat: UNKNOWN",
    ):
        registry.get("UNKNOWN")


def test_registry_copies_supplied_mapping():
    calculator = FakeRiskCalculator()

    calculators = {
        "TICK": calculator,
    }

    registry = RiskCalculatorRegistry(
        calculators=calculators,
    )

    calculators.clear()

    assert registry.get("TICK") is calculator