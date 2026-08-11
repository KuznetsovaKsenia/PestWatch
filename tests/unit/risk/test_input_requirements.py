import pytest

from app.domain import RiskInputCapability
from app.risk import (
    RiskInputRequirements,
    RiskInputRequirementsNotFoundError,
)


@pytest.mark.parametrize(
    ("threat_code", "expected"),
    [
        (
            "TICK",
            frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SATURATION_DEFICIT,
            }),
        ),
        (
            "CABBAGE_APHID",
            frozenset({
                RiskInputCapability.CURRENT_WEATHER,
            }),
        ),
        (
            "COLORADO_BEETLE",
            frozenset({
                RiskInputCapability.CURRENT_WEATHER,
                RiskInputCapability.SOIL_TEMPERATURE_10CM,
            }),
        ),
        (
            "CODLING_MOTH",
            frozenset({
                RiskInputCapability.DEGREE_DAYS_10C,
            }),
        ),
    ],
)
def test_returns_requirements_for_threat(
    threat_code,
    expected,
):
    requirements = RiskInputRequirements()

    result = requirements.get(threat_code)

    assert result == expected


def test_returns_immutable_requirements():
    requirements = RiskInputRequirements()

    result = requirements.get("TICK")

    assert isinstance(result, frozenset)


def test_raises_for_unknown_threat():
    requirements = RiskInputRequirements()

    with pytest.raises(
        RiskInputRequirementsNotFoundError,
        match=(
            "No risk input requirements registered "
            "for threat: UNKNOWN"
        ),
    ):
        requirements.get("UNKNOWN")