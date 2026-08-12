import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.seed.threat_catalog import seed_threat_catalog


SCENARIOS = [
    ("DEMO_A", "HUMAN", {
        "TICK": ("CALCULATED", "LOW", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
            "SATURATION_DEFICIT": "NOT_MATCHED",
        }),
    }),
    ("DEMO_A", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "LOW", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "LOW", {
            "SOIL_TEMPERATURE_10CM": "NOT_MATCHED",
        }),
    }),
    ("DEMO_A", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "LOW", {
            "DEGREE_DAYS_ABOVE_10C": "NOT_MATCHED",
        }),
    }),
    ("DEMO_B", "HUMAN", {
        "TICK": ("CALCULATED", "ELEVATED", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
            "SATURATION_DEFICIT": "MATCHED",
        }),
    }),
    ("DEMO_B", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "LOW", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "HIGH", {
            "SOIL_TEMPERATURE_10CM": "MATCHED",
        }),
    }),
    ("DEMO_B", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "LOW", {
            "DEGREE_DAYS_ABOVE_10C": "NOT_MATCHED",
        }),
    }),
    ("DEMO_C", "HUMAN", {
        "TICK": ("CALCULATED", "ELEVATED", {
            "AIR_TEMPERATURE": "MATCHED",
            "SATURATION_DEFICIT": "NOT_MATCHED",
        }),
    }),
    ("DEMO_C", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "LOW", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "HIGH", {
            "SOIL_TEMPERATURE_10CM": "MATCHED",
        }),
    }),
    ("DEMO_C", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "HIGH", {
            "DEGREE_DAYS_ABOVE_10C": "MATCHED",
        }),
    }),
    ("DEMO_D", "HUMAN", {
        "TICK": ("CALCULATED", "HIGH", {
            "AIR_TEMPERATURE": "MATCHED",
            "SATURATION_DEFICIT": "MATCHED",
        }),
    }),
    ("DEMO_D", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "HIGH", {
            "AIR_TEMPERATURE": "MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "HIGH", {
            "SOIL_TEMPERATURE_10CM": "MATCHED",
        }),
    }),
    ("DEMO_D", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "HIGH", {
            "DEGREE_DAYS_ABOVE_10C": "MATCHED",
        }),
    }),
    ("DEMO_E", "HUMAN", {
        "TICK": ("CALCULATED", "HIGH", {
            "AIR_TEMPERATURE": "MATCHED",
            "SATURATION_DEFICIT": "MATCHED",
        }),
    }),
    ("DEMO_E", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "HIGH", {
            "AIR_TEMPERATURE": "MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "HIGH", {
            "SOIL_TEMPERATURE_10CM": "MATCHED",
        }),
    }),
    ("DEMO_E", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "HIGH", {
            "DEGREE_DAYS_ABOVE_10C": "MATCHED",
        }),
    }),
    ("DEMO_F", "HUMAN", {
        "TICK": ("CALCULATED", "ELEVATED", {
            "AIR_TEMPERATURE": "MATCHED",
            "SATURATION_DEFICIT": "NOT_MATCHED",
        }),
    }),
    ("DEMO_F", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("CALCULATED", "LOW", {
            "AIR_TEMPERATURE": "NOT_MATCHED",
        }),
        "COLORADO_BEETLE": ("CALCULATED", "LOW", {
            "SOIL_TEMPERATURE_10CM": "NOT_MATCHED",
        }),
    }),
    ("DEMO_F", "GARDEN", {
        "CODLING_MOTH": ("CALCULATED", "LOW", {
            "DEGREE_DAYS_ABOVE_10C": "NOT_MATCHED",
        }),
    }),
    ("DEMO_G", "HUMAN", {
        "TICK": ("INSUFFICIENT_DATA", None, {
            "AIR_TEMPERATURE": "MISSING",
            "SATURATION_DEFICIT": "MISSING",
        }),
    }),
    ("DEMO_G", "VEGETABLE_GARDEN", {
        "CABBAGE_APHID": ("INSUFFICIENT_DATA", None, {
            "AIR_TEMPERATURE": "MISSING",
        }),
        "COLORADO_BEETLE": ("INSUFFICIENT_DATA", None, {
            "SOIL_TEMPERATURE_10CM": "MISSING",
        }),
    }),
    ("DEMO_G", "GARDEN", {
        "CODLING_MOTH": ("INSUFFICIENT_DATA", None, {
            "DEGREE_DAYS_ABOVE_10C": "MISSING",
        }),
    }),
]


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        seed_threat_catalog()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.parametrize(
    ("scenario_id", "profile", "expected_results"),
    SCENARIOS,
)
def test_demo_scenario_runs_through_full_pipeline(
    client,
    scenario_id,
    profile,
    expected_results,
):
    response = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": scenario_id,
            "profile": profile,
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["success"] is True
    assert body["data"]["profile"] == profile
    assert body["data"]["assessment_date"] == "2026-05-13"

    actual_results = {
        result["threat_code"]: result
        for result in body["data"]["risk_results"]
    }

    assert set(actual_results) == set(expected_results)

    for threat_code, (
        expected_status,
        expected_level,
        expected_factors,
    ) in expected_results.items():
        actual = actual_results[threat_code]

        assert actual["status"] == expected_status
        assert actual["risk_level"] == expected_level

        actual_factors = {
            factor["factor"]: factor
            for factor in actual["factors"]
        }

        assert set(actual_factors) == set(expected_factors)

        for factor_code, expected_state in expected_factors.items():
            assert (
                actual_factors[factor_code]["state"]
                == expected_state
            )


def test_demo_soil_boundaries_are_preserved_in_snapshot(client):
    cases = [
        ("DEMO_A", 10.9),
        ("DEMO_B", 11.0),
        ("DEMO_C", 11.1),
    ]

    for scenario_id, expected in cases:
        response = client.post(
            "/api/assessments/demo",
            json={
                "scenario_id": scenario_id,
                "profile": "VEGETABLE_GARDEN",
            },
        )

        assert response.status_code == 201

        estimate = (
            response.get_json()["data"]
            ["input_snapshot"]
            ["soil_temperature_10cm_estimate"]
        )

        assert estimate is not None
        assert estimate["temperature"] == pytest.approx(expected)


@pytest.mark.parametrize(
    ("scenario_id", "expected_total"),
    [
        ("DEMO_B", 129.9),
        ("DEMO_C", 130.0),
        ("DEMO_D", 130.1),
    ],
)
def test_demo_degree_day_boundaries_are_preserved(
    client,
    scenario_id,
    expected_total,
):
    response = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": scenario_id,
            "profile": "GARDEN",
        },
    )

    assert response.status_code == 201

    degree_days = (
        response.get_json()["data"]
        ["input_snapshot"]["degree_days_10c"]
    )

    assert degree_days is not None
    assert degree_days["total"] == pytest.approx(expected_total)
