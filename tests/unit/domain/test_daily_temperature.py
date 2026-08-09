from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from app.domain import DailyTemperature


def test_daily_temperature_can_be_created():
    observation = DailyTemperature(
        date=date(2026, 5, 1),
        mean_temperature=12.5,
    )

    assert observation.date == date(2026, 5, 1)
    assert observation.mean_temperature == 12.5


def test_daily_temperature_allows_missing_temperature():
    observation = DailyTemperature(
        date=date(2026, 5, 1),
        mean_temperature=None,
    )

    assert observation.mean_temperature is None


@pytest.mark.parametrize(
    "temperature",
    [
        0.0,
        -5.0,
    ],
)
def test_daily_temperature_preserves_valid_values(
    temperature,
):
    observation = DailyTemperature(
        date=date(2026, 5, 1),
        mean_temperature=temperature,
    )

    assert observation.mean_temperature == temperature


def test_daily_temperature_is_immutable():
    observation = DailyTemperature(
        date=date(2026, 5, 1),
        mean_temperature=12.5,
    )

    with pytest.raises(FrozenInstanceError):
        observation.mean_temperature = 13.0