from datetime import date

import pytest

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
)
from app.weather import DegreeDaysCalculator


def observations(*temperatures):
    return tuple(
        DailyTemperature(
            date=date(2026, 5, 1 + index),
            mean_temperature=temperature,
        )
        for index, temperature in enumerate(temperatures)
    )


@pytest.mark.parametrize(
    ("temperatures", "expected_total"),
    [
        ((5.0, 8.0, 9.0), 0.0),
        ((10.0,), 0.0),
        ((11.0,), 1.0),
        ((12.0, 15.0), 7.0),
        ((9.0, 10.0, 12.0, 15.0), 7.0),
        ((20.0, 20.0), 20.0),
        ((-20.0, -5.0, 0.0), 0.0),
    ],
)
def test_calculator_accumulates_degree_days(
    temperatures,
    expected_total,
):
    calculator = DegreeDaysCalculator()

    result = calculator.calculate(
        observations(*temperatures)
    )

    assert result is not None
    assert result.total == pytest.approx(expected_total)


@pytest.mark.parametrize(
    ("temperature", "expected_total"),
    [
        (9.9, 0.0),
        (10.0, 0.0),
        (10.1, 0.1),
    ],
)
def test_calculator_respects_base_temperature_boundary(
    temperature,
    expected_total,
):
    calculator = DegreeDaysCalculator()

    result = calculator.calculate(
        observations(temperature)
    )

    assert result is not None
    assert result.total == pytest.approx(expected_total)


def test_calculator_returns_none_for_empty_series():
    calculator = DegreeDaysCalculator()

    result = calculator.calculate(())

    assert result is None


def test_calculator_returns_none_for_missing_temperature():
    calculator = DegreeDaysCalculator()

    result = calculator.calculate(
        observations(
            12.0,
            None,
            15.0,
        )
    )

    assert result is None


def test_calculator_rejects_unsorted_dates():
    calculator = DegreeDaysCalculator()

    data = (
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=15.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="ordered chronologically",
    ):
        calculator.calculate(data)


def test_calculator_rejects_duplicate_dates():
    calculator = DegreeDaysCalculator()

    data = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=15.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="without duplicate dates",
    ):
        calculator.calculate(data)


def test_calculator_returns_none_for_calendar_gap():
    calculator = DegreeDaysCalculator()

    data = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 3),
            mean_temperature=15.0,
        ),
    )

    result = calculator.calculate(data)

    assert result is None


def test_result_contains_provenance():
    calculator = DegreeDaysCalculator()

    data = observations(
        12.0,
        15.0,
    )

    result = calculator.calculate(data)

    assert result is not None
    assert result.base_temperature == 10.0
    assert result.period_start == date(2026, 5, 1)
    assert result.period_end == date(2026, 5, 2)
    assert result.observations == data
    assert (
        result.method
        == DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
    )


def test_calculation_is_deterministic():
    calculator = DegreeDaysCalculator()

    data = observations(
        12.0,
        15.0,
        20.0,
    )

    first = calculator.calculate(data)
    second = calculator.calculate(data)

    assert first == second