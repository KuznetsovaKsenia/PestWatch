import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.domain import Threat
from app.repositories import ThreatRepository
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


def test_repository_returns_all_threats(app):
    with app.app_context():
        repository = ThreatRepository()

        threats = repository.get_all()

        assert len(threats) == 4
        assert all(
            isinstance(threat, Threat)
            for threat in threats
        )


def test_repository_returns_threats_ordered_by_name(app):
    with app.app_context():
        repository = ThreatRepository()

        threats = repository.get_all()

        names = [
            threat.name
            for threat in threats
        ]

        assert names == sorted(names)


def test_repository_returns_threat_by_code(app):
    with app.app_context():
        repository = ThreatRepository()

        threat = repository.get_by_code("TICK")

        assert threat is not None
        assert isinstance(threat, Threat)
        assert threat.code == "TICK"
        assert threat.name == "Иксодовые клещи"
        assert threat.category == "HUMAN"
        assert threat.active is True


def test_repository_returns_none_for_unknown_code(app):
    with app.app_context():
        repository = ThreatRepository()

        threat = repository.get_by_code("UNKNOWN")

        assert threat is None


def test_repository_does_not_expose_orm_model(app):
    with app.app_context():
        repository = ThreatRepository()

        threat = repository.get_by_code("TICK")

        assert isinstance(threat, Threat)
        assert not isinstance(threat, db.Model)

def test_repository_returns_threat_details(app):
    with app.app_context():
        repository = ThreatRepository()

        details = repository.get_details_by_code("TICK")

        assert details is not None
        assert details.threat.code == "TICK"

        assert len(details.recommendations) == 3
        assert [
            recommendation.priority
            for recommendation in details.recommendations
        ] == [1, 2, 3]

        assert len(details.sources) == 1
        assert details.sources[0].organization == (
            "Управление Роспотребнадзора по Рязанской области"
        )


def test_repository_returns_no_details_for_unknown_code(app):
    with app.app_context():
        repository = ThreatRepository()

        details = repository.get_details_by_code("UNKNOWN")

        assert details is None

def test_repository_returns_threats_by_category(app):
    with app.app_context():
        repository = ThreatRepository()

        threats = repository.get_by_category(
            "VEGETABLE_GARDEN",
        )

        assert {
            threat.code
            for threat in threats
        } == {
            "COLORADO_BEETLE",
            "CABBAGE_APHID",
        }

        assert all(
            threat.category == "VEGETABLE_GARDEN"
            for threat in threats
        )

def test_repository_returns_category_threats_ordered_by_name(app):
    with app.app_context():
        repository = ThreatRepository()

        threats = repository.get_by_category(
            "VEGETABLE_GARDEN",
        )

        names = [
            threat.name
            for threat in threats
        ]

        assert names == sorted(names)

def test_repository_returns_empty_list_for_unknown_category(app):
    with app.app_context():
        repository = ThreatRepository()

        threats = repository.get_by_category(
            "UNKNOWN",
        )

        assert threats == []