from app.domain import (
    RiskLevel,
    RiskResult,
    RiskStatus,
)
from app.risk import SingleThreatRiskEvaluator


class FakeContextPreparer:
    def __init__(self, context):
        self.context = context
        self.calls = []

    def prepare(
        self,
        threat_code,
        *,
        weather=None,
        historical_temperatures=None,
        degree_days_season_started=None,
    ):
        self.calls.append(
            (
                threat_code,
                weather,
                historical_temperatures,
                degree_days_season_started,
            )
        )

        return self.context


class FakeCalculator:
    def __init__(self):
        self.received_context = None

    def evaluate(
        self,
        context,
    ):
        self.received_context = context

        return ()


class FakeRegistry:
    def __init__(
        self,
        calculator,
    ):
        self.calculator = calculator
        self.received_code = None

    def get(
        self,
        threat_code,
    ):
        self.received_code = threat_code

        return self.calculator


class FakeEngine:
    def __init__(
        self,
        result,
    ):
        self.result = result
        self.received_threat_code = None
        self.received_factors = None

    def evaluate(
        self,
        *,
        threat_code,
        factors,
    ):
        self.received_threat_code = (
            threat_code
        )
        self.received_factors = factors

        return self.result


def create_result():
    return RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.HIGH,
        factors=(),
        explanation="Calculated.",
    )


def create_evaluator():
    context = object()
    calculator = FakeCalculator()
    result = create_result()

    preparer = FakeContextPreparer(
        context
    )

    registry = FakeRegistry(
        calculator
    )

    engine = FakeEngine(
        result
    )

    evaluator = SingleThreatRiskEvaluator(
        context_preparer=preparer,
        calculator_registry=registry,
        engine=engine,
    )

    return (
        evaluator,
        context,
        calculator,
        registry,
        engine,
        result,
    )


def test_evaluate_with_context_returns_result_and_context():
    (
        evaluator,
        context,
        _,
        _,
        _,
        result,
    ) = create_evaluator()

    (
        actual_result,
        actual_context,
    ) = evaluator.evaluate_with_context(
        "TICK"
    )

    assert actual_result is result
    assert actual_context is context


def test_existing_evaluate_contract_still_returns_only_result():
    (
        evaluator,
        _,
        _,
        _,
        _,
        result,
    ) = create_evaluator()

    actual = evaluator.evaluate(
        "TICK"
    )

    assert actual is result
