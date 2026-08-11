from datetime import date

import pytest

from app.domain import DailyTemperature
from app.risk import CodlingMothSeasonStartDetector


def observations(*temperatures):
    return tuple(
        DailyTemperature(
            date=date(2026, 4, 1 + index),
            mean_temperature=temperature,
        )
        for index, temperature in enumerate(temperatures)
    )


def test_detects_first_three_consecutive_days_above_10c():
    detector = CodlingMothSeasonStartDetector()

    result = detector.find_start(
        observations(
            8.0,
            11.0,
            12.0,
            13.0,
            9.0,
        )
    )

    assert result == date(2026, 4, 2)


def test_exactly_10c_does_not_start_streak():
    detector = CodlingMothSeasonStartDetector()

    result = detector.find_start(
        observations(
            10.0,
            11.0,
            12.0,
            13.0,
        )
    )

    assert result == date(2026, 4, 2)


def test_missing_temperature_breaks_streak():
    detector = CodlingMothSeasonStartDetector()

    result = detector.find_start(
        observations(
            11.0,
            12.0,
            None,
            11.0,
            12.0,
            13.0,
        )
    )

    assert result == date(2026, 4, 4)


def test_calendar_gap_breaks_streak():
    detector = CodlingMothSeasonStartDetector()

    data = (
        DailyTemperature(
            date=date(2026, 4, 1),
            mean_temperature=11.0,
        ),
        DailyTemperature(
            date=date(2026, 4, 2),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 4, 4),
            mean_temperature=13.0,
        ),
        DailyTemperature(
            date=date(2026, 4, 5),
            mean_temperature=14.0,
        ),
        DailyTemperature(
            date=date(2026, 4, 6),
            mean_temperature=15.0,
        ),
    )

    result = detector.find_start(data)

    assert result == date(2026, 4, 4)


def test_returns_none_when_season_has_not_started():
    detector = CodlingMothSeasonStartDetector()

    result = detector.find_start(
        observations(
            5.0,
            11.0,
            9.0,
            12.0,
            10.0,
        )
    )

    assert result is None


def test_rejects_unsorted_observations():
    detector = CodlingMothSeasonStartDetector()

    data = (
        DailyTemperature(
            date=date(2026, 4, 2),
            mean_temperature=11.0,
        ),
        DailyTemperature(
            date=date(2026, 4, 1),
            mean_temperature=12.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="ordered chronologically",
    ):
        detector.find_start(data)
