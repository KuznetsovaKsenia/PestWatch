from datetime import date, datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.config.settings import TestConfig
from app.models import AssessmentModel


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


def create_assessment_model():
    return AssessmentModel(
        created_at=datetime(
            2026,
            8,
            11,
            14,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile="VEGETABLE_GARDEN",
        location_name="Москва",
        location_region="Москва",
        location_country="Россия",
        location_latitude=55.7558,
        location_longitude=37.6173,
        historical_start_date=None,
    )


def test_assessment_table_is_created(app):
    with app.app_context():
        inspector = inspect(db.engine)

        table_names = set(
            inspector.get_table_names()
        )

        assert "assessments" in table_names


def test_assessment_can_be_persisted(app):
    with app.app_context():
        assessment = create_assessment_model()

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(AssessmentModel)
        ).scalar_one()

        assert saved.id is not None

        assert saved.created_at == datetime(
            2026,
            8,
            11,
            14,
            0,
        )

        assert saved.assessment_date == date(
            2026,
            8,
            11,
        )

        assert saved.profile == "VEGETABLE_GARDEN"

        assert saved.location_name == "Москва"
        assert saved.location_region == "Москва"
        assert saved.location_country == "Россия"

        assert saved.location_latitude == pytest.approx(
            55.7558
        )

        assert saved.location_longitude == pytest.approx(
            37.6173
        )

        assert saved.historical_start_date is None


def test_historical_start_date_can_be_persisted(app):
    with app.app_context():
        assessment = create_assessment_model()

        assessment.historical_start_date = date(
            2026,
            5,
            1,
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(AssessmentModel)
        ).scalar_one()

        assert (
            saved.historical_start_date
            == date(
                2026,
                5,
                1,
            )
        )


def test_required_assessment_metadata_cannot_be_null(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()
        assessment.profile = None

        db.session.add(assessment)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()