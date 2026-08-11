from datetime import date, datetime

from app.domain import (
    DailyTemperature,
    RiskContext,
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskResult,
    RiskStatus,
    WeatherData,
)
from app.risk import SingleThreatRiskEvaluator


class FakeRiskContextPreparer:
    def __init__(self, context):
        self.context = context
        self.received_threat_code = None
        self.received_weather = None
        self.received_historical_temperatures = None
        self.received_degree_days_season_started = None

    def prepare(
        self,
        threat_code,
        *,
        weather=None,
        historical_temperatures=None,
        degree_days_season_started=None,
    ):
        self.received_threat_code = threat_code
        self.received_weather = weather
        self.received_historical_temperatures = (
            historical_temperatures
        )
        self.received_degree_days_season_started = (
            degree_days_season_started
        )

        return self.context


class FakeRiskCalculator:
    def __init__(self, factors):
        self.factors = factors
        self.received_context = None

    def evaluate(self, context):
        self.received_context = context

        return self.factors


class FakeRiskCalculatorRegistry:
    def __init__(self, calculator):
        self.calculator = calculator
        self.received_threat_code = None

    def get(self, threat_code):
        self.received_threat_code = threat_code

        return self.calculator


class FakeRiskEngine:
    def __init__(self, result):
        self.result = result
        self.received_threat_code = None
        self.received_factors = None

    def evaluate(
        self,
        threat_code,
        factors,
    ):
        self.received_threat_code = threat_code
        self.received_factors = factors

        return self.result


def create_weather():
    return WeatherData(
        observed_at=datetime(2026, 8, 11, 12, 0),
        temperature=20.0,
        humidity=60.0,
        precipitation=0.0,
        wind_speed=2.0,
        soil_temperature=18.0,
        soil_temperature_6cm=16.0,
        soil_temperature_18cm=10.0,
    )


def create_factor():
    return RiskFactorResult(
        factor="AIR_TEMPERATURE",
        state=RiskFactorState.MATCHED,
        actual_value=20.0,
        expected=">= 10 °C",
        explanation="Test factor.",
        required=True,
    )


def create_result(factors):
    return RiskResult(
        threat_code="TICK",
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.HIGH,
        factors=factors,
        explanation="Calculated.",
    )


def create_evaluator():
    context = RiskContext(
        weather=create_weather(),
    )

    factors = (
        create_factor(),
    )

    result = create_result(factors)

    preparer = FakeRiskContextPreparer(
        context,
    )
    calculator = FakeRiskCalculator(
        factors,
    )
    registry = FakeRiskCalculatorRegistry(
        calculator,
    )
    engine = FakeRiskEngine(
        result,
    )

    evaluator = SingleThreatRiskEvaluator(
        context_preparer=preparer,
        calculator_registry=registry,
        engine=engine,
    )

    return (
        evaluator,
        preparer,
        calculator,
        registry,
        engine,
        context,
        factors,
        result,
    )


def test_evaluator_passes_inputs_to_context_preparer():
    (
        evaluator,
        preparer,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = create_evaluator()

    weather = create_weather()

    historical_temperatures = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
    )

    evaluator.evaluate(
        "TICK",
        weather=weather,
        historical_temperatures=(
            historical_temperatures
        ),
    )

    assert preparer.received_threat_code == "TICK"
    assert preparer.received_weather is weather
    assert (
        preparer.received_historical_temperatures
        is historical_temperatures
    )
    assert (
        preparer.received_degree_days_season_started
        is None
    )


def test_evaluator_gets_calculator_by_threat_code():
    (
        evaluator,
        _,
        _,
        registry,
        _,
        _,
        _,
        _,
    ) = create_evaluator()

    evaluator.evaluate(
        "TICK",
        weather=create_weather(),
    )

    assert registry.received_threat_code == "TICK"


def test_evaluator_passes_context_to_calculator():
    (
        evaluator,
        _,
        calculator,
        _,
        _,
        context,
        _,
        _,
    ) = create_evaluator()

    evaluator.evaluate(
        "TICK",
        weather=create_weather(),
    )

    assert calculator.received_context is context


def test_evaluator_passes_factors_to_engine():
    (
        evaluator,
        _,
        _,
        _,
        engine,
        _,
        factors,
        _,
    ) = create_evaluator()

    evaluator.evaluate(
        "TICK",
        weather=create_weather(),
    )

    assert engine.received_threat_code == "TICK"
    assert engine.received_factors is factors


def test_evaluator_returns_engine_result():
    (
        evaluator,
        _,
        _,
        _,
        _,
        _,
        _,
        expected_result,
    ) = create_evaluator()

    result = evaluator.evaluate(
        "TICK",
        weather=create_weather(),
    )

    assert result is expected_result
