import pytest

from app import create_app
from app.config.settings import TestConfig
from app import create_app, db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_can_be_created(app):
    assert app is not None


def test_home_page_returns_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_home_page_contains_project_name(client):
    response = client.get("/")

    assert b"PestWatch" in response.data


def test_database_uses_in_memory_sqlite(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_database_can_be_initialized(app):
    with app.app_context():
        db.create_all()

        assert db.engine.url.drivername == "sqlite"
        assert str(db.engine.url) == "sqlite:///:memory:"

        db.drop_all()