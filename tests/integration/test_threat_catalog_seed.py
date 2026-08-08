import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.models import (
    RecommendationModel,
    SourceModel,
    ThreatModel,
)
from app.seed.threat_catalog import seed_threat_catalog


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


def test_seed_creates_four_threats(app):
    with app.app_context():
        seed_threat_catalog()

        threats = db.session.execute(
            db.select(ThreatModel)
        ).scalars().all()

        assert len(threats) == 4


def test_seed_creates_expected_threat_codes(app):
    with app.app_context():
        seed_threat_catalog()

        threats = db.session.execute(
            db.select(ThreatModel)
        ).scalars().all()

        codes = {
            threat.code
            for threat in threats
        }

        assert codes == {
            "TICK",
            "COLORADO_BEETLE",
            "CABBAGE_APHID",
            "CODLING_MOTH",
        }


def test_seed_creates_recommendations_for_every_threat(app):
    with app.app_context():
        seed_threat_catalog()

        threats = db.session.execute(
            db.select(ThreatModel)
        ).scalars().all()

        for threat in threats:
            assert len(threat.recommendations) >= 2


def test_seed_creates_sources_for_every_threat(app):
    with app.app_context():
        seed_threat_catalog()

        threats = db.session.execute(
            db.select(ThreatModel)
        ).scalars().all()

        for threat in threats:
            assert len(threat.sources) >= 1


def test_seed_creates_expected_number_of_recommendations(app):
    with app.app_context():
        seed_threat_catalog()

        recommendations = db.session.execute(
            db.select(RecommendationModel)
        ).scalars().all()

        assert len(recommendations) == 12


def test_seed_creates_four_sources(app):
    with app.app_context():
        seed_threat_catalog()

        sources = db.session.execute(
            db.select(SourceModel)
        ).scalars().all()

        assert len(sources) == 4


def test_seed_is_idempotent(app):
    with app.app_context():
        seed_threat_catalog()
        seed_threat_catalog()

        threats = db.session.execute(
            db.select(ThreatModel)
        ).scalars().all()

        recommendations = db.session.execute(
            db.select(RecommendationModel)
        ).scalars().all()

        sources = db.session.execute(
            db.select(SourceModel)
        ).scalars().all()

        assert len(threats) == 4
        assert len(recommendations) == 12
        assert len(sources) == 4


def test_tick_seed_contains_expected_related_data(app):
    with app.app_context():
        seed_threat_catalog()

        tick = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == "TICK"
            )
        ).scalar_one()

        assert tick.name == "Иксодовые клещи"
        assert tick.category == "HUMAN"
        assert tick.active is True

        assert len(tick.recommendations) == 3
        assert [
            recommendation.priority
            for recommendation in tick.recommendations
        ] == [1, 2, 3]

        assert len(tick.sources) == 1
        assert (
            tick.sources[0].organization
            == "Управление Роспотребнадзора по Рязанской области"
        )