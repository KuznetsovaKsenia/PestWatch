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


def test_get_threats_returns_200(client):
    response = client.get("/api/threats")

    assert response.status_code == 200


def test_get_threats_returns_four_threats(client):
    response = client.get("/api/threats")
    body = response.get_json()

    assert body["success"] is True
    assert len(body["data"]) == 4


def test_get_threats_contains_expected_codes(client):
    response = client.get("/api/threats")
    body = response.get_json()

    codes = {
        threat["code"]
        for threat in body["data"]
    }

    assert codes == {
        "TICK",
        "COLORADO_BEETLE",
        "CABBAGE_APHID",
        "CODLING_MOTH",
    }


def test_get_tick_returns_details(client):
    response = client.get("/api/threats/TICK")
    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True

    data = body["data"]

    assert data["code"] == "TICK"
    assert data["name"] == "Иксодовые клещи"
    assert data["category"] == "HUMAN"
    assert data["active"] is True

    assert len(data["recommendations"]) == 3
    assert len(data["sources"]) == 1


def test_get_tick_recommendations_are_ordered(client):
    response = client.get("/api/threats/TICK")
    body = response.get_json()

    priorities = [
        recommendation["priority"]
        for recommendation in body["data"]["recommendations"]
    ]

    assert priorities == [1, 2, 3]


def test_get_tick_source_contains_required_fields(client):
    response = client.get("/api/threats/TICK")
    body = response.get_json()

    source = body["data"]["sources"][0]

    assert source["title"]
    assert source["organization"]
    assert source["url"]
    assert source["description"]


def test_get_unknown_threat_returns_404(client):
    response = client.get("/api/threats/UNKNOWN")
    body = response.get_json()

    assert response.status_code == 404
    assert body == {
        "success": False,
        "error": {
            "code": "THREAT_NOT_FOUND",
            "message": "Threat not found.",
        },
    }