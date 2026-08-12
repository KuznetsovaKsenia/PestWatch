from datetime import date, datetime

import pytest
from sqlalchemy import inspect

from app import create_app, db
from app.config.settings import TestConfig
from app.models import (
    AssessmentInputSnapshotModel,
    AssessmentModel,
)


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
            15,
            30,
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


def test_snapshot_table_is_created(app):
    with app.app_context():
        inspector = inspect(db.engine)

        assert (
            "assessment_input_snapshots"
            in inspector.get_table_names()
        )


def test_current_weather_snapshot_can_be_persisted(app):
    with app.app_context():
        assessment = create_assessment_model()

        assessment.input_snapshot = (
            AssessmentInputSnapshotModel(
                weather_observed_at=datetime(
                    2026,
                    8,
                    11,
                    12,
                    0,
                ),
                weather_temperature=25.5,
                weather_humidity=65.0,
                weather_precipitation=0.0,
                weather_wind_speed=2.0,
                weather_soil_temperature=18.0,
                weather_soil_temperature_6cm=16.0,
                weather_soil_temperature_18cm=10.0,
                saturation_deficit_mm_hg=1.25,
            )
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(
                AssessmentInputSnapshotModel
            )
        ).scalar_one()

        assert saved.assessment_id == assessment.id

        assert saved.weather_observed_at == datetime(
            2026,
            8,
            11,
            12,
            0,
        )

        assert saved.weather_temperature == pytest.approx(
            25.5
        )

        assert saved.weather_humidity == pytest.approx(
            65.0
        )

        assert (
            saved.weather_soil_temperature_6cm
            == pytest.approx(16.0)
        )

        assert (
            saved.weather_soil_temperature_18cm
            == pytest.approx(10.0)
        )

        assert (
            saved.saturation_deficit_mm_hg
            == pytest.approx(1.25)
        )


def test_soil_temperature_estimate_can_be_persisted(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        assessment.input_snapshot = (
            AssessmentInputSnapshotModel(
                soil_estimate_depth_cm=10.0,
                soil_estimate_temperature=14.0,
                soil_estimate_source_depths=[
                    6.0,
                    18.0,
                ],
                soil_estimate_source_temperatures=[
                    16.0,
                    10.0,
                ],
                soil_estimate_method=(
                    "LINEAR_INTERPOLATION"
                ),
            )
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(
                AssessmentInputSnapshotModel
            )
        ).scalar_one()

        assert saved.soil_estimate_depth_cm == 10.0

        assert (
            saved.soil_estimate_temperature
            == pytest.approx(14.0)
        )

        assert saved.soil_estimate_source_depths == [
            6.0,
            18.0,
        ]

        assert (
            saved.soil_estimate_source_temperatures
            == [
                16.0,
                10.0,
            ]
        )

        assert (
            saved.soil_estimate_method
            == "LINEAR_INTERPOLATION"
        )


def test_degree_days_snapshot_can_be_persisted(app):
    with app.app_context():
        assessment = create_assessment_model()

        assessment.input_snapshot = (
            AssessmentInputSnapshotModel(
                degree_days_base_temperature=10.0,
                degree_days_total=130.0,
                degree_days_period_start=date(
                    2026,
                    5,
                    1,
                ),
                degree_days_period_end=date(
                    2026,
                    5,
                    13,
                ),
                degree_days_method=(
                    "DAILY_MEAN_ABOVE_BASE"
                ),
                degree_days_observations=[
                    {
                        "date": "2026-05-10",
                        "mean_temperature": 20.0,
                    },
                    {
                        "date": "2026-05-11",
                        "mean_temperature": 21.0,
                    },
                ],
                historical_observations=[
                    {
                        "date": "2026-05-01",
                        "mean_temperature": 20.0,
                    },
                    {
                        "date": "2026-05-02",
                        "mean_temperature": 20.0,
                    },
                ],
            )
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(
                AssessmentInputSnapshotModel
            )
        ).scalar_one()

        assert (
            saved.degree_days_base_temperature
            == pytest.approx(10.0)
        )

        assert saved.degree_days_total == pytest.approx(
            130.0
        )

        assert saved.degree_days_period_start == date(
            2026,
            5,
            1,
        )

        assert saved.degree_days_period_end == date(
            2026,
            5,
            13,
        )

        assert (
            saved.degree_days_method
            == "DAILY_MEAN_ABOVE_BASE"
        )

        assert saved.degree_days_observations == [
            {
                "date": "2026-05-10",
                "mean_temperature": 20.0,
            },
            {
                "date": "2026-05-11",
                "mean_temperature": 21.0,
            },
        ]

        assert saved.historical_observations == [
            {
                "date": "2026-05-01",
                "mean_temperature": 20.0,
            },
            {
                "date": "2026-05-02",
                "mean_temperature": 20.0,
            },
        ]


def test_deleting_assessment_deletes_input_snapshot(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        assessment.input_snapshot = (
            AssessmentInputSnapshotModel(
                weather_temperature=20.0,
            )
        )

        db.session.add(assessment)
        db.session.commit()

        assessment_id = assessment.id

        db.session.delete(assessment)
        db.session.commit()

        assert (
            db.session.get(
                AssessmentModel,
                assessment_id,
            )
            is None
        )

        assert (
            db.session.execute(
                db.select(
                    AssessmentInputSnapshotModel
                )
            ).scalars().all()
            == []
        )