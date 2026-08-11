from datetime import date, datetime

import pytest
from sqlalchemy import inspect

from app import create_app, db
from app.config.settings import TestConfig
from app.models import (
    AssessmentModel,
    RiskFactorResultModel,
    RiskResultModel,
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


def create_risk_result_model():
    return RiskResultModel(
        threat_code="COLORADO_BEETLE",
        status="CALCULATED",
        risk_level="HIGH",
        explanation="Calculated.",
    )


def create_factor_model():
    return RiskFactorResultModel(
        factor="SOIL_TEMPERATURE_10CM",
        state="MATCHED",
        actual_value=14.0,
        expected=">= 13 °C",
        explanation="Matched.",
        required=True,
    )


def test_risk_result_tables_are_created(app):
    with app.app_context():
        inspector = inspect(db.engine)

        table_names = set(
            inspector.get_table_names()
        )

        assert "risk_results" in table_names
        assert "risk_factor_results" in table_names


def test_risk_result_can_be_persisted_for_assessment(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        result = create_risk_result_model()

        assessment.risk_results.append(
            result
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(RiskResultModel)
        ).scalar_one()

        assert saved.assessment_id == assessment.id
        assert saved.threat_code == "COLORADO_BEETLE"
        assert saved.status == "CALCULATED"
        assert saved.risk_level == "HIGH"
        assert saved.explanation == "Calculated."


def test_risk_factor_can_be_persisted_for_risk_result(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        result = create_risk_result_model()
        factor = create_factor_model()

        result.factors.append(
            factor
        )

        assessment.risk_results.append(
            result
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(RiskFactorResultModel)
        ).scalar_one()

        assert saved.risk_result_id == result.id
        assert (
            saved.factor
            == "SOIL_TEMPERATURE_10CM"
        )
        assert saved.state == "MATCHED"
        assert saved.actual_value == pytest.approx(
            14.0
        )
        assert saved.expected == ">= 13 °C"
        assert saved.explanation == "Matched."
        assert saved.required is True


def test_risk_level_can_be_null_for_error_result(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        result = RiskResultModel(
            threat_code="COLORADO_BEETLE",
            status="ERROR",
            risk_level=None,
            explanation="Weather timeout.",
        )

        assessment.risk_results.append(
            result
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(RiskResultModel)
        ).scalar_one()

        assert saved.status == "ERROR"
        assert saved.risk_level is None
        assert (
            saved.explanation
            == "Weather timeout."
        )


def test_factor_actual_value_can_be_null(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        result = create_risk_result_model()

        factor = RiskFactorResultModel(
            factor="AIR_TEMPERATURE",
            state="MISSING",
            actual_value=None,
            expected=">= 10 °C",
            explanation="Temperature is missing.",
            required=True,
        )

        result.factors.append(
            factor
        )

        assessment.risk_results.append(
            result
        )

        db.session.add(assessment)
        db.session.commit()

        saved = db.session.execute(
            db.select(RiskFactorResultModel)
        ).scalar_one()

        assert saved.state == "MISSING"
        assert saved.actual_value is None


def test_deleting_assessment_deletes_results_and_factors(
    app,
):
    with app.app_context():
        assessment = create_assessment_model()

        result = create_risk_result_model()
        result.factors.append(
            create_factor_model()
        )

        assessment.risk_results.append(
            result
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
                db.select(RiskResultModel)
            ).scalars().all()
            == []
        )

        assert (
            db.session.execute(
                db.select(RiskFactorResultModel)
            ).scalars().all()
            == []
        )