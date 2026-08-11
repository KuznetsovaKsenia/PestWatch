import pytest

from app.weather import SaturationDeficitCalculator


@pytest.mark.parametrize(
    ("temperature", "humidity", "expected"),
    [
        (18.0, 91.0, 1.3613736321850247),
        (18.0, 40.0, 9.075824214566834),
        (10.0, 80.0, 1.8408030376197366),
    ],
)
def test_calculates_saturation_deficit(
    temperature,
    humidity,
    expected,
):
    result = SaturationDeficitCalculator().calculate(
        temperature=temperature,
        humidity=humidity,
    )

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("temperature", "humidity"),
    [
        (None, 80.0),
        (18.0, None),
        (None, None),
    ],
)
def test_returns_none_when_required_observation_missing(
    temperature,
    humidity,
):
    result = SaturationDeficitCalculator().calculate(
        temperature=temperature,
        humidity=humidity,
    )

    assert result is None
