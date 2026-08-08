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


def test_threat_catalog_returns_200(client):
    response = client.get("/threats")

    assert response.status_code == 200


@pytest.mark.parametrize(
    "threat_name",
    [
        "Иксодовые клещи",
        "Колорадский жук",
        "Капустная тля",
        "Яблонная плодожорка",
    ],
)
def test_threat_catalog_contains_supported_threats(
    client,
    threat_name,
):
    response = client.get("/threats")

    assert threat_name.encode("utf-8") in response.data


def test_threat_catalog_contains_project_name(client):
    response = client.get("/threats")

    assert b"PestWatch" in response.data