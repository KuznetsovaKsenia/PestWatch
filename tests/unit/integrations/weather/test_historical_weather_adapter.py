from datetime import date

import pytest

from app.domain import DailyTemperature
from app.integrations.weather import (
    HistoricalWeatherAdapter,
    WeatherDataError,
)


def test_adapter_maps_complete_payload():
    payload = {
        "daily": {
            "time": [
                "2026-05-01",
                "2026-05-02",
                "2026-05-03",
            ],
            "temperature_2m_mean": [
                12.5,
                14.0,
                9.0,
            ],
        }
    }

    adapter = HistoricalWeatherAdapter()

    observations = adapter.to_daily_temperatures(payload)

    assert observations == (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=12.5,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=14.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 3),
            mean_temperature=9.0,
        ),
    )


@pytest.mark.parametrize(
    "temperature",
    [
        0.0,
        -5.0,
        None,
    ],
)
def test_adapter_preserves_temperature_value(
    temperature,
):
    payload = {
        "daily": {
            "time": ["2026-05-01"],
            "temperature_2m_mean": [temperature],
        }
    }

    adapter = HistoricalWeatherAdapter()

    observations = adapter.to_daily_temperatures(payload)

    assert observations[0].mean_temperature == temperature


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"daily": None},
        {"daily": []},
    ],
)
def test_adapter_rejects_missing_or_invalid_daily(
    payload,
):
    adapter = HistoricalWeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="does not contain daily data",
    ):
        adapter.to_daily_temperatures(payload)


@pytest.mark.parametrize(
    "daily",
    [
        {},
        {
            "temperature_2m_mean": [12.0],
        },
        {
            "time": "2026-05-01",
            "temperature_2m_mean": [12.0],
        },
    ],
)
def test_adapter_rejects_missing_or_invalid_dates(
    daily,
):
    adapter = HistoricalWeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="does not contain daily dates",
    ):
        adapter.to_daily_temperatures(
            {"daily": daily}
        )


@pytest.mark.parametrize(
    "daily",
    [
        {
            "time": ["2026-05-01"],
        },
        {
            "time": ["2026-05-01"],
            "temperature_2m_mean": 12.0,
        },
    ],
)
def test_adapter_rejects_missing_or_invalid_temperatures(
    daily,
):
    adapter = HistoricalWeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="does not contain daily mean temperatures",
    ):
        adapter.to_daily_temperatures(
            {"daily": daily}
        )


def test_adapter_rejects_arrays_with_different_lengths():
    payload = {
        "daily": {
            "time": [
                "2026-05-01",
                "2026-05-02",
            ],
            "temperature_2m_mean": [
                12.0,
            ],
        }
    }

    adapter = HistoricalWeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="different lengths",
    ):
        adapter.to_daily_temperatures(payload)


@pytest.mark.parametrize(
    "invalid_date",
    [
        "not-a-date",
        "2026-13-01",
        123,
        [],
    ],
)
def test_adapter_rejects_invalid_date(
    invalid_date,
):
    payload = {
        "daily": {
            "time": [invalid_date],
            "temperature_2m_mean": [12.0],
        }
    }

    adapter = HistoricalWeatherAdapter()

    with pytest.raises(
        WeatherDataError,
        match="contains invalid date",
    ):
        adapter.to_daily_temperatures(payload)