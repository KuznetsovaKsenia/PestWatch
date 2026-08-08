import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.config.settings import TestConfig
from app.models import (
    RecommendationModel,
    SourceModel,
    ThreatModel,
)


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


def test_threat_catalog_tables_are_created(app):
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = set(inspector.get_table_names())

        assert {
            "threats",
            "sources",
            "recommendations",
            "threat_source",
        }.issubset(table_names)


def test_threat_code_is_unique(app):
    with app.app_context():
        first = ThreatModel(
            code="TICK",
            name="Иксодовые клещи",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        second = ThreatModel(
            code="TICK",
            name="Другой вид",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        db.session.add(first)
        db.session.commit()

        db.session.add(second)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


def test_threat_relations_can_be_persisted(app):
    with app.app_context():
        threat = ThreatModel(
            code="TICK",
            name="Иксодовые клещи",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        source = SourceModel(
            title="Источник",
            organization="Организация",
            url="https://example.test/source",
            description="Описание источника",
        )

        recommendation = RecommendationModel(
            text="Проводить самоосмотр после прогулки.",
            priority=1,
        )

        threat.sources.append(source)
        threat.recommendations.append(recommendation)

        db.session.add(threat)
        db.session.commit()

        saved = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == "TICK"
            )
        ).scalar_one()

        assert saved.code == "TICK"

        assert len(saved.sources) == 1
        assert saved.sources[0].title == "Источник"
        assert saved.sources[0].organization == "Организация"

        assert len(saved.recommendations) == 1
        assert (
            saved.recommendations[0].text
            == "Проводить самоосмотр после прогулки."
        )
        assert saved.recommendations[0].priority == 1


def test_one_source_can_be_linked_to_multiple_threats(app):
    with app.app_context():
        source = SourceModel(
            title="Общий источник",
            organization="Организация",
            url="https://example.test/common-source",
            description="Источник для нескольких видов",
        )

        tick = ThreatModel(
            code="TICK",
            name="Иксодовые клещи",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        aphid = ThreatModel(
            code="CABBAGE_APHID",
            name="Капустная тля",
            category="VEGETABLE_GARDEN",
            description="Описание",
            active=True,
        )

        tick.sources.append(source)
        aphid.sources.append(source)

        db.session.add_all([tick, aphid])
        db.session.commit()

        saved_source = db.session.execute(
            db.select(SourceModel).where(
                SourceModel.title == "Общий источник"
            )
        ).scalar_one()

        threat_codes = {
            threat.code
            for threat in saved_source.threats
        }

        assert threat_codes == {
            "TICK",
            "CABBAGE_APHID",
        }


def test_recommendations_are_ordered_by_priority(app):
    with app.app_context():
        threat = ThreatModel(
            code="TICK",
            name="Иксодовые клещи",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        threat.recommendations.extend(
            [
                RecommendationModel(
                    text="Рекомендация с приоритетом 3",
                    priority=3,
                ),
                RecommendationModel(
                    text="Рекомендация с приоритетом 1",
                    priority=1,
                ),
                RecommendationModel(
                    text="Рекомендация с приоритетом 2",
                    priority=2,
                ),
            ]
        )

        db.session.add(threat)
        db.session.commit()

        saved = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == "TICK"
            )
        ).scalar_one()

        priorities = [
            recommendation.priority
            for recommendation in saved.recommendations
        ]

        assert priorities == [1, 2, 3]