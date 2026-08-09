from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
)


def create_result() -> DegreeDaysResult:
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=15.0,
        ),
    )

    return DegreeDaysResult(
        base_temperature=10.0,
        total=7.0,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 2),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
        ),
    )


def test_degree_days_result_can_be_created():
    result = create_result()

    assert result.base_temperature == 10.0
    assert result.total == 7.0
    assert result.period_start == date(2026, 5, 1)
    assert result.period_end == date(2026, 5, 2)
    assert len(result.observations) == 2
    assert (
        result.method
        == DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
    )


def test_degree_days_method_has_stable_value():
    assert (
        DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE.value
        == "DAILY_MEAN_ABOVE_BASE"
    )


def test_degree_days_result_preserves_observations():
    result = create_result()

    assert result.observations == (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=15.0,
        ),
    )


def test_degree_days_result_is_immutable():
    result = create_result()

    with pytest.raises(FrozenInstanceError):
        result.total = 8.0