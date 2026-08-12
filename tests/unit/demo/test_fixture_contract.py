from datetime import date

import pytest

from app.demo import DemoScenarioRegistry
from app.risk import CodlingMothSeasonStartDetector
from app.weather import (
    DegreeDaysCalculator,
    SaturationDeficitCalculator,
    SoilTemperatureEstimator,
)


@pytest.mark.parametrize(
    (
        "scenario_id",
        "expected_deficit",
    ),
    [
        ("DEMO_A", 5.4882212155581955),
        ("DEMO_B", 3.658814143705464),
        ("DEMO_C", 6.238767468355762),
        ("DEMO_D", 3.7665784559764663),
        ("DEMO_E", 4.672535742672662),
        ("DEMO_F", 5.877053090614046),
        ("DEMO_G", None),
    ],
)
def test_fixture_saturation_deficit(
    scenario_id,
    expected_deficit,
):
    scenario = DemoScenarioRegistry().get(
        scenario_id
    )
    weather = scenario.current_weather

    actual = SaturationDeficitCalculator().calculate(
        temperature=weather.temperature,
        humidity=weather.humidity,
    )

    if expected_deficit is None:
        assert actual is None
    else:
        assert actual == pytest.approx(
            expected_deficit
        )


@pytest.mark.parametrize(
    (
        "scenario_id",
        "expected_temperature",
    ),
    [
        ("DEMO_A", 10.9),
        ("DEMO_B", 11.0),
        ("DEMO_C", 11.1),
        ("DEMO_D", 11.0),
        ("DEMO_E", 11.0),
        ("DEMO_F", 10.8),
        ("DEMO_G", None),
    ],
)
def test_fixture_soil_temperature_at_10cm(
    scenario_id,
    expected_temperature,
):
    scenario = DemoScenarioRegistry().get(
        scenario_id
    )
    weather = scenario.current_weather

    estimate = SoilTemperatureEstimator().estimate_at_10cm(
        temperature_6cm=(
            weather.soil_temperature_6cm
        ),
        temperature_18cm=(
            weather.soil_temperature_18cm
        ),
    )

    if expected_temperature is None:
        assert estimate is None
    else:
        assert estimate is not None
        assert estimate.temperature == pytest.approx(
            expected_temperature
        )


@pytest.mark.parametrize(
    (
        "scenario_id",
        "expected_start",
        "expected_total",
    ),
    [
        ("DEMO_A", None, None),
        ("DEMO_B", date(2026, 5, 1), 129.9),
        ("DEMO_C", date(2026, 5, 1), 130.0),
        ("DEMO_D", date(2026, 5, 1), 130.1),
        ("DEMO_E", date(2026, 5, 1), 156.0),
        ("DEMO_F", date(2026, 5, 1), 100.0),
        ("DEMO_G", date(2026, 5, 1), None),
    ],
)
def test_fixture_codling_moth_season_and_degree_days(
    scenario_id,
    expected_start,
    expected_total,
):
    scenario = DemoScenarioRegistry().get(
        scenario_id
    )
    observations = (
        scenario.historical_temperatures
    )

    season_start = (
        CodlingMothSeasonStartDetector()
        .find_start(observations)
    )

    assert season_start == expected_start

    if season_start is None:
        assert expected_total is None
        return

    season_observations = tuple(
        observation
        for observation in observations
        if observation.date >= season_start
    )

    degree_days = DegreeDaysCalculator().calculate(
        season_observations
    )

    if expected_total is None:
        assert degree_days is None
    else:
        assert degree_days is not None
        assert degree_days.total == pytest.approx(
            expected_total
        )
