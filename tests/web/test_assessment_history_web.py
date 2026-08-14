from datetime import date, datetime

import pytest
from flask import Flask

from app.controllers.assessment_history_web import (
    create_assessment_history_web,
)
from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskResult,
    RiskStatus,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
)
from app.domain.assessment_source import AssessmentSource
from app.domain.assessment_summary import AssessmentSummary
from app.domain.daily_temperature import DailyTemperature
from app.domain.location import Location
from app.domain.user_profile import UserProfile


class FakeAssessmentHistoryService:
    def __init__(
        self,
        history=(),
        assessment=None,
    ):
        self.history = history
        self.assessment = assessment
        self.calls = 0
        self.received_assessment_id = None

    def get_history(self):
        self.calls += 1
        return self.history

    def get_assessment(
        self,
        assessment_id,
    ):
        self.received_assessment_id = (
            assessment_id
        )

        return self.assessment


def create_summary(
    *,
    assessment_id=42,
    source=AssessmentSource.REAL,
    profile=UserProfile.HUMAN,
    location_name="Москва",
    location_region="Москва",
):
    return AssessmentSummary(
        id=assessment_id,
        created_at=datetime(
            2026,
            8,
            12,
            18,
            45,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=profile,
        location=Location(
            name=location_name,
            region=location_region,
            country="Россия",
            latitude=55.7558,
            longitude=37.6173,
        ),
        source=source,
    )


def create_full_assessment():
    return Assessment(
        id=42,
        created_at=datetime(
            2026,
            8,
            12,
            18,
            45,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=UserProfile.HUMAN,
        location=Location(
            name="Москва",
            region="Москва",
            country="Россия",
            latitude=55.7558,
            longitude=37.6173,
        ),
        source=AssessmentSource.REAL,
        historical_start_date=None,
        risk_results=(
            RiskResult(
                threat_code="TICK",
                status=RiskStatus.CALCULATED,
                risk_level=RiskLevel.HIGH,
                factors=(),
                explanation=(
                    "Расчёт выполнен."
                ),
            ),
        ),
        input_snapshot=(
            AssessmentInputSnapshot()
        ),
    )


def create_evidence_assessment():
    observations = (
        DailyTemperature(
            date=date(2026, 5, 1),
            mean_temperature=20.0,
        ),
        DailyTemperature(
            date=date(2026, 5, 2),
            mean_temperature=21.0,
        ),
    )

    soil_estimate = SoilTemperatureEstimate(
        depth_cm=10.0,
        temperature=15.666666666666666,
        source_depths_cm=(
            6.0,
            18.0,
        ),
        source_temperatures=(
            16.0,
            10.0,
        ),
        method=(
            SoilTemperatureEstimateMethod
            .LINEAR_INTERPOLATION
        ),
    )

    degree_days = DegreeDaysResult(
        base_temperature=10.0,
        total=21.0,
        period_start=date(
            2026,
            5,
            1,
        ),
        period_end=date(
            2026,
            5,
            2,
        ),
        observations=observations,
        method=(
            DegreeDaysCalculationMethod
            .DAILY_MEAN_ABOVE_BASE
        ),
    )

    factor = RiskFactorResult(
        factor="SOIL_TEMPERATURE_10CM",
        state=RiskFactorState.MATCHED,
        actual_value=15.666666666666666,
        expected=">= 11 °C",
        explanation=(
            "Температурное условие выполнено."
        ),
        required=True,
    )

    return Assessment(
        id=43,
        created_at=datetime(
            2026,
            8,
            12,
            19,
            0,
        ),
        assessment_date=date(
            2026,
            8,
            12,
        ),
        profile=(
            UserProfile.VEGETABLE_GARDEN
        ),
        location=Location(
            name="Калуга",
            region="Калужская область",
            country="Россия",
            latitude=54.5138,
            longitude=36.2612,
        ),
        source=AssessmentSource.REAL,
        historical_start_date=date(
            2026,
            5,
            1,
        ),
        risk_results=(
            RiskResult(
                threat_code="COLORADO_BEETLE",
                status=RiskStatus.CALCULATED,
                risk_level=RiskLevel.HIGH,
                factors=(factor,),
                explanation=(
                    "Оценка выполнена."
                ),
            ),
        ),
        input_snapshot=(
            AssessmentInputSnapshot(
                current_weather=None,
                soil_temperature_10cm_estimate=(
                    soil_estimate
                ),
                degree_days_10c=degree_days,
                saturation_deficit_mm_hg=1.25,
                historical_observations=(
                    observations
                ),
            )
        ),
    )


@pytest.fixture
def history_client():
    def factory(
        history=(),
        assessment=None,
    ):
        app = Flask(
            __name__,
            template_folder=(
                "../../app/templates"
            ),
        )

        app.config["TESTING"] = True

        history_service = (
            FakeAssessmentHistoryService(
                history=history,
                assessment=assessment,
            )
        )

        app.register_blueprint(
            create_assessment_history_web(
                history_service=history_service,
            )
        )

        @app.get("/")
        def index():
            return "index"

        app.add_url_rule(
            "/threats",
            endpoint=(
                "threat_web.get_threat_catalog"
            ),
            view_func=lambda: "threats",
        )

        return (
            app.test_client(),
            history_service,
        )

    return factory


def test_history_page_returns_200(
    history_client,
):
    client, service = history_client()

    response = client.get(
        "/history"
    )

    assert response.status_code == 200
    assert service.calls == 1


def test_history_page_shows_empty_state(
    history_client,
):
    client, _ = history_client()

    response = client.get(
        "/history"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert "История пока пуста" in text
    assert "Выполнить оценку" in text


def test_history_page_shows_real_assessment(
    history_client,
):
    client, _ = history_client(
        history=(
            create_summary(),
        )
    )

    response = client.get(
        "/history"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert "Москва" in text
    assert "Человек" in text
    assert "12.08.2026" in text
    assert "Обычная оценка" in text


def test_history_page_shows_demo_assessment(
    history_client,
):
    client, _ = history_client(
        history=(
            create_summary(
                assessment_id=7,
                source=AssessmentSource.DEMO,
                profile=UserProfile.GARDEN,
                location_name="Тула",
                location_region=(
                    "Тульская область"
                ),
            ),
        )
    )

    response = client.get(
        "/history"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert "Тула" in text
    assert "Тульская область" in text
    assert "Сад" in text
    assert "Демо" in text


def test_history_page_preserves_service_order(
    history_client,
):
    client, _ = history_client(
        history=(
            create_summary(
                assessment_id=2,
                location_name="Москва",
            ),
            create_summary(
                assessment_id=1,
                location_name="Тула",
            ),
        )
    )

    response = client.get(
        "/history"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert (
        text.index("Москва")
        < text.index("Тула")
    )


def test_history_page_contains_detail_link(
    history_client,
):
    client, _ = history_client(
        history=(
            create_summary(),
        )
    )

    response = client.get(
        "/history"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert (
        'href="/history/42"'
        in text
    )
    assert "Открыть" in text


def test_history_detail_returns_404_when_missing(
    history_client,
):
    client, service = history_client(
        assessment=None
    )

    response = client.get(
        "/history/999"
    )

    assert response.status_code == 404

    assert (
        service.received_assessment_id
        == 999
    )


def test_history_detail_shows_stored_assessment(
    history_client,
):
    assessment = (
        create_full_assessment()
    )

    client, service = history_client(
        assessment=assessment
    )

    response = client.get(
        "/history/42"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert response.status_code == 200

    assert "Москва" in text
    assert "Человек" in text
    assert "Обычная оценка" in text
    assert "Иксодовые клещи" in text
    assert "ВЫСОКИЙ РИСК" in text
    assert "Расчёт выполнен." in text
    assert (
        "Исторический результат"
        in text
    )

    assert (
        service.received_assessment_id
        == 42
    )


def test_history_detail_shows_persisted_factor_evidence(
    history_client,
):
    client, _ = history_client(
        assessment=(
            create_evidence_assessment()
        )
    )

    response = client.get(
        "/history/43"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert response.status_code == 200

    assert "Факторы оценки" in text
    assert (
        "Температура почвы на глубине 10 см"
        in text
    )
    assert "Условие выполнено" in text
    assert "15,7 °C" in text
    assert "от 11 °C" in text
    assert (
        "Температурное условие выполнено."
        in text
    )


def test_history_detail_shows_persisted_snapshot(
    history_client,
):
    client, _ = history_client(
        assessment=(
            create_evidence_assessment()
        )
    )

    response = client.get(
        "/history/43"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert response.status_code == 200

    assert (
        "Сохранённый снимок данных"
        in text
    )

    assert "Температура почвы" in text
    assert "15,7 °C" in text
    assert "16 °C" in text
    assert "10 °C" in text
    assert (
        "Линейная интерполяция"
        in text
    )

    assert (
        "Температурный сезон"
        in text
    )
    assert "01.05.2026" in text
    assert "02.05.2026" in text
    assert "21 градусо-дней" in text
    assert "2" in text

    assert (
        "Начало температурного сезона"
        in text
    )


def test_history_detail_formats_persisted_values(
    history_client,
):
    client, _ = history_client(
        assessment=(
            create_evidence_assessment()
        )
    )

    response = client.get(
        "/history/43"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert response.status_code == 200

    assert "15,7 °C" in text

    assert (
        "15.666666666666666"
        not in text
    )

    assert "10 см" in text
    assert "10.0 см" not in text

    assert "от 11 °C" in text
    assert "&gt;= 11 °C" not in text


def test_history_detail_formats_degree_days(
    history_client,
):
    client, _ = history_client(
        assessment=(
            create_evidence_assessment()
        )
    )

    response = client.get(
        "/history/43"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert response.status_code == 200

    assert (
        "21 градусо-дней"
        in text
    )

    assert "10 °C" in text