from datetime import date, datetime

import pytest

from app.domain import (
    Assessment,
    Location,
    RiskLevel,
    RiskResult,
    RiskStatus,
    UserProfile,
)


def create_location():
    return Location(
        name="Москва",
        region="Москва",
        country="Россия",
        latitude=55.7558,
        longitude=37.6173,
    )


def create_risk_result(
    threat_code="TICK",
):
    return RiskResult(
        threat_code=threat_code,
        status=RiskStatus.CALCULATED,
        risk_level=RiskLevel.HIGH,
        factors=(),
        explanation="Calculated.",
    )


def test_assessment_can_be_created_before_persistence():
    assessment = Assessment(
        id=None,
        created_at=datetime(
            2026,
            8,
            11,
            13,
            30,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.HUMAN,
        location=create_location(),
        historical_start_date=None,
        risk_results=(
            create_risk_result(),
        ),
    )

    assert assessment.id is None


def test_assessment_preserves_identity_and_metadata():
    created_at = datetime(
        2026,
        8,
        11,
        13,
        30,
    )

    assessment_date = date(
        2026,
        8,
        11,
    )

    location = create_location()

    assessment = Assessment(
        id=42,
        created_at=created_at,
        assessment_date=assessment_date,
        profile=UserProfile.HUMAN,
        location=location,
        historical_start_date=None,
        risk_results=(
            create_risk_result(),
        ),
    )

    assert assessment.id == 42
    assert assessment.created_at == created_at
    assert assessment.assessment_date == assessment_date
    assert assessment.profile == UserProfile.HUMAN
    assert assessment.location is location


def test_assessment_preserves_risk_results():
    results = (
        create_risk_result(
            "COLORADO_BEETLE"
        ),
        create_risk_result(
            "CABBAGE_APHID"
        ),
    )

    assessment = Assessment(
        id=42,
        created_at=datetime(
            2026,
            8,
            11,
            13,
            30,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.VEGETABLE_GARDEN,
        location=create_location(),
        historical_start_date=None,
        risk_results=results,
    )

    assert assessment.risk_results is results


def test_assessment_can_preserve_historical_period():
    start_date = date(
        2026,
        5,
        1,
    )

    assessment = Assessment(
        id=42,
        created_at=datetime(
            2026,
            8,
            11,
            13,
            30,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.GARDEN,
        location=create_location(),
        historical_start_date=start_date,
        risk_results=(
            create_risk_result(
                "CODLING_MOTH"
            ),
        ),
    )

    assert (
        assessment.historical_start_date
        == start_date
    )


def test_historical_start_date_cannot_be_after_assessment_date():
    with pytest.raises(
        ValueError,
        match=(
            "Historical start date cannot be "
            "after assessment date"
        ),
    ):
        Assessment(
            id=None,
            created_at=datetime(
                2026,
                8,
                11,
                13,
                30,
            ),
            assessment_date=date(
                2026,
                5,
                1,
            ),
            profile=UserProfile.GARDEN,
            location=create_location(),
            historical_start_date=date(
                2026,
                8,
                11,
            ),
            risk_results=(
                create_risk_result(
                    "CODLING_MOTH"
                ),
            ),
        )


def test_assessment_allows_empty_risk_results():
    assessment = Assessment(
        id=None,
        created_at=datetime(
            2026,
            8,
            11,
            13,
            30,
        ),
        assessment_date=date(
            2026,
            8,
            11,
        ),
        profile=UserProfile.HUMAN,
        location=create_location(),
        historical_start_date=None,
        risk_results=(),
    )

    assert assessment.risk_results == ()