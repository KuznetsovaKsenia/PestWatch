from dataclasses import FrozenInstanceError

import pytest

from app.domain import (
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
)


def create_estimate() -> SoilTemperatureEstimate:
    return SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=14.0,
        source_depths_cm=(6.0, 18.0),
        source_temperatures=(16.0, 10.0),
        method=SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION,
    )


def test_soil_temperature_estimate_can_be_created():
    estimate = create_estimate()

    assert estimate.depth_cm == 10.0
    assert estimate.temperature == 14.0
    assert estimate.source_depths_cm == (6.0, 18.0)
    assert estimate.source_temperatures == (16.0, 10.0)
    assert (
        estimate.method
        == SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
    )


def test_linear_interpolation_method_has_stable_value():
    assert (
        SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION.value
        == "LINEAR_INTERPOLATION"
    )


def test_soil_temperature_estimate_is_immutable():
    estimate = create_estimate()

    with pytest.raises(FrozenInstanceError):
        estimate.temperature = 15.0