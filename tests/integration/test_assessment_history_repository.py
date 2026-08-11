from datetime import date, datetime

from app import create_app, db
from app.config.settings import TestConfig
from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    Location,
    UserProfile,
)
from app.domain.assessment_summary import AssessmentSummary
from app.repositories import AssessmentRepository


def create_location(
    name,
    latitude,
    longitude,
):
    return Location(
        name=name,
        region="Москва",
        country="Россия",
        latitude=latitude,
        longitude=longitude,
    )


def create_assessment(
    *,
    created_at,
    location,
    profile,
):
    return Assessment(
        id=None,
        created_at=created_at,
        assessment_date=created_at.date(),
        profile=profile,
        location=location,
        historical_start_date=None,
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
        risk_results=(),
    )


def test_repository_returns_empty_history():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        try:
            repository = AssessmentRepository()

            history = repository.get_all()

            assert history == ()

        finally:
            db.session.remove()
            db.drop_all()


def test_repository_returns_history_newest_first():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        try:
            repository = AssessmentRepository()

            older = repository.save(
                create_assessment(
                    created_at=datetime(
                        2026,
                        8,
                        10,
                        12,
                        0,
                    ),
                    location=create_location(
                        "Москва",
                        55.7558,
                        37.6173,
                    ),
                    profile=UserProfile.HUMAN,
                )
            )

            newer = repository.save(
                create_assessment(
                    created_at=datetime(
                        2026,
                        8,
                        11,
                        12,
                        0,
                    ),
                    location=create_location(
                        "Тула",
                        54.1961,
                        37.6182,
                    ),
                    profile=(
                        UserProfile.VEGETABLE_GARDEN
                    ),
                )
            )

            history = repository.get_all()

            assert tuple(
                item.id
                for item in history
            ) == (
                newer.id,
                older.id,
            )

        finally:
            db.session.remove()
            db.drop_all()


def test_repository_returns_assessment_summaries():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        try:
            repository = AssessmentRepository()

            saved = repository.save(
                create_assessment(
                    created_at=datetime(
                        2026,
                        8,
                        11,
                        12,
                        0,
                    ),
                    location=create_location(
                        "Тула",
                        54.1961,
                        37.6182,
                    ),
                    profile=UserProfile.GARDEN,
                )
            )

            history = repository.get_all()

            assert len(history) == 1

            summary = history[0]

            assert isinstance(
                summary,
                AssessmentSummary,
            )

            assert summary.id == saved.id

            assert summary.created_at == datetime(
                2026,
                8,
                11,
                12,
                0,
            )

            assert summary.assessment_date == date(
                2026,
                8,
                11,
            )

            assert (
                summary.profile
                == UserProfile.GARDEN
            )

            assert summary.location.name == "Тула"

            assert (
                summary.location.latitude
                == 54.1961
            )

            assert (
                summary.location.longitude
                == 37.6182
            )

        finally:
            db.session.remove()
            db.drop_all()