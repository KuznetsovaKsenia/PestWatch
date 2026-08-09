import pytest

from app.domain import SoilTemperatureEstimateMethod
from app.weather import SoilTemperatureEstimator


@pytest.mark.parametrize(
    (
        "temperature_6cm",
        "temperature_18cm",
        "expected_temperature",
    ),
    [
        (16.0, 10.0, 14.0),
        (10.0, 16.0, 12.0),
        (13.0, 13.0, 13.0),
        (0.0, 6.0, 2.0),
        (-4.0, 2.0, -2.0),
    ],
)
def test_estimate_at_10cm(
    temperature_6cm,
    temperature_18cm,
    expected_temperature,
):
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=temperature_6cm,
        temperature_18cm=temperature_18cm,
    )

    assert estimate is not None
    assert estimate.temperature == pytest.approx(
        expected_temperature
    )


@pytest.mark.parametrize(
    (
        "temperature_6cm",
        "temperature_18cm",
    ),
    [
        (None, 14.0),
        (14.0, None),
        (None, None),
    ],
)
def test_missing_source_temperature_returns_none(
    temperature_6cm,
    temperature_18cm,
):
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=temperature_6cm,
        temperature_18cm=temperature_18cm,
    )

    assert estimate is None


def test_estimate_contains_target_depth():
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=16.0,
        temperature_18cm=10.0,
    )

    assert estimate is not None
    assert estimate.depth_cm == 10.0


def test_estimate_contains_source_depths():
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=16.0,
        temperature_18cm=10.0,
    )

    assert estimate is not None
    assert estimate.source_depths_cm == (6.0, 18.0)


def test_estimate_contains_source_temperatures():
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=16.0,
        temperature_18cm=10.0,
    )

    assert estimate is not None
    assert estimate.source_temperatures == (16.0, 10.0)


def test_estimate_contains_calculation_method():
    estimator = SoilTemperatureEstimator()

    estimate = estimator.estimate_at_10cm(
        temperature_6cm=16.0,
        temperature_18cm=10.0,
    )

    assert estimate is not None
    assert (
        estimate.method
        == SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
    )