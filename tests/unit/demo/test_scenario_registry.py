from datetime import date

import pytest

from app.demo import (
    DemoScenarioNotFoundError,
    DemoScenarioRegistry,
)


def test_registry_contains_seven_scenarios():
    registry = DemoScenarioRegistry()

    assert len(registry.get_all()) == 7


def test_registry_preserves_expected_order():
    registry = DemoScenarioRegistry()

    assert [
        scenario.location.name
        for scenario in registry.get_all()
    ] == [
        "Архангельск",
        "Казань",
        "Омск",
        "Пермь",
        "Тула",
        "Курск",
        "Томск",
    ]


def test_registry_uses_fixed_assessment_date():
    registry = DemoScenarioRegistry()

    assert {
        scenario.assessment_date
        for scenario in registry.get_all()
    } == {
        date(2026, 5, 13),
    }


def test_registry_locations_are_unique():
    registry = DemoScenarioRegistry()

    locations = [
        (
            scenario.location.name,
            scenario.location.region,
            scenario.location.country,
            scenario.location.latitude,
            scenario.location.longitude,
        )
        for scenario in registry.get_all()
    ]

    assert len(locations) == len(set(locations))


def test_registry_returns_scenario_by_id():
    registry = DemoScenarioRegistry()

    scenario = registry.get("DEMO_B")

    assert scenario.location.name == "Казань"


def test_registry_rejects_unknown_scenario():
    registry = DemoScenarioRegistry()

    with pytest.raises(
        DemoScenarioNotFoundError
    ):
        registry.get("UNKNOWN")
