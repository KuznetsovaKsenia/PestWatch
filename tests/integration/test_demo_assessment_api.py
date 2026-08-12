import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.seed.threat_catalog import seed_threat_catalog


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


def test_demo_assessment_endpoint_returns_assessment(client):
    response = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": "DEMO_B",
            "profile": "HUMAN",
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["success"] is True
    assert body["data"]["profile"] == "HUMAN"
    assert body["data"]["assessment_date"] == "2026-05-13"
    assert body["data"]["location"]["name"] == "Казань"
    assert body["data"]["risk_results"][0]["threat_code"] == "TICK"


def test_demo_assessment_uses_fixed_scenario_date(client):
    response = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": "DEMO_C",
            "profile": "GARDEN",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["data"]["assessment_date"] == "2026-05-13"


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"scenario_id": "DEMO_A"},
        {"profile": "HUMAN"},
        {"scenario_id": "", "profile": "HUMAN"},
        {"scenario_id": "DEMO_A", "profile": "UNKNOWN"},
    ],
)
def test_demo_assessment_rejects_invalid_input(client, payload):
    response = client.post(
        "/api/assessments/demo",
        json=payload,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_REQUEST"


def test_demo_assessment_rejects_unknown_scenario(client):
    response = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": "DEMO_UNKNOWN",
            "profile": "HUMAN",
        },
    )

    assert response.status_code == 400
    assert (
        response.get_json()["error"]["code"]
        == "DEMO_SCENARIO_NOT_FOUND"
    )


def test_demo_assessment_is_saved_to_history(client):
    created = client.post(
        "/api/assessments/demo",
        json={
            "scenario_id": "DEMO_D",
            "profile": "HUMAN",
        },
    )

    assert created.status_code == 201
    assessment_id = created.get_json()["data"]["id"]

    fetched = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert fetched.status_code == 200

    data = fetched.get_json()["data"]

    assert data["id"] == assessment_id
    assert data["location"]["name"] == "Пермь"
    assert data["profile"] == "HUMAN"
