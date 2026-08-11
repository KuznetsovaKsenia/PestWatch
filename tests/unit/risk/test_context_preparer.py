from datetime import date, datetime

import pytest

from app.domain import (
    DailyTemperature,
    RiskInputCapability,
    WeatherData,
)
from app.risk import (
    RiskContextPreparer,
    RiskInputUnavailableError,
)


class FakeRiskInputRequirements:
    def __init__(self, capabilities):
        self.capabilities = capabilities
        self.received_threat_code = None

    def get(self, threat_code):
        self.received_threat_code = threat_code
        return self.capabilities


class FakeSoilTemperatureEstimator:
    def __init__(self, estimate=None):
        self.estimate = estimate
        self.received_temperature_6cm = None
        self.received_temperature_18cm = None

    def estimate_at_10cm(
        self,
        temperature_6cm,
        temperature_18cm,
    ):
        self.received_temperature_6cm = temperature_6cm
        self.received_temperature_18cm = temperature_18cm

        return self.estimate


class FakeDegreeDaysCalculator:
    def __init__(self, result=None):
        self.result = result
        self.received_observations = None

    def calculate(self, observations):
        self.received_observations = observations

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


def create_preparer(
    capabilities,
    *,
    estimate=None,
    degree_days=None,
):
    return RiskContextPreparer(
        requirements=FakeRiskInputRequirements(
            capabilities,
        ),
        soil_temperature_estimator=(
            FakeSoilTemperatureEstimator(
                estimate=estimate,
            )
        ),
        degree_days_calculator=(
            FakeDegreeDaysCalculator(
                result=degree_days,
            )
        ),
    )


def test_preparer_preserves_current_weather():
    weather = create_weather()

    preparer = create_preparer(
        frozenset({
            RiskInputCapability.CURRENT_WEATHER,
        }),
    )

    context = preparer.prepare(
        "TICK",
        weather=weather,
    )

    assert context.weather is weather
    assert context.soil_temperature_10cm_estimate is None
    assert context.degree_days_10c is None


def test_preparer_requires_current_weather():
    preparer = create_preparer(
        frozenset({
            RiskInputCapability.CURRENT_WEATHER,
        }),
    )

    with pytest.raises(
        RiskInputUnavailableError,
        match="Current weather input is unavailable",
    ):
        preparer.prepare(
            "TICK",
        )


def test_preparer_builds_soil_temperature_estimate():
    weather = create_weather()
    estimate = object()

    estimator = FakeSoilTemperatureEstimator(
        estimate=estimate,
    )

    preparer = RiskContextPreparer(
        requirements=FakeRiskInputRequirements(
            frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
        ),
        soil_temperature_estimator=estimator,
        degree_days_calculator=FakeDegreeDaysCalculator(),
    )

    context = preparer.prepare(
        "COLORADO_BEETLE",
        weather=weather,
    )

    assert context.soil_temperature_10cm_estimate is estimate
    assert estimator.received_temperature_6cm == 16.0
    assert estimator.received_temperature_18cm == 10.0


def test_preparer_builds_degree_days_without_current_weather():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
    )

    degree_days = object()

    calculator = FakeDegreeDaysCalculator(
        result=degree_days,
    )

    preparer = RiskContextPreparer(
        requirements=FakeRiskInputRequirements(
            frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        ),
        soil_temperature_estimator=(
            FakeSoilTemperatureEstimator()
        ),
        degree_days_calculator=calculator,
    )

    context = preparer.prepare(
        "CODLING_MOTH",
        historical_temperatures=observations,
    )

    assert context.weather is None
    assert context.degree_days_10c is degree_days
    assert calculator.received_observations is observations


def test_preparer_requires_historical_temperatures():
    preparer = create_preparer(
        frozenset({
            RiskInputCapability.DEGREE_DAYS_10C,
        }),
    )

    with pytest.raises(
        RiskInputUnavailableError,
        match="Historical temperature input is unavailable",
    ):
        preparer.prepare(
            "CODLING_MOTH",
        )


def test_empty_historical_observations_are_valid_input():
    observations = ()

    calculator = FakeDegreeDaysCalculator(
        result=None,
    )

    preparer = RiskContextPreparer(
        requirements=FakeRiskInputRequirements(
            frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        ),
        soil_temperature_estimator=(
            FakeSoilTemperatureEstimator()
        ),
        degree_days_calculator=calculator,
    )

    context = preparer.prepare(
        "CODLING_MOTH",
        historical_temperatures=observations,
    )

    assert calculator.received_observations == ()
    assert context.degree_days_10c is None