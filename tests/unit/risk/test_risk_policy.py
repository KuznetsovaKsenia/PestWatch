import pytest

from app.domain import (
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskStatus,
)
from app.risk import RiskPolicy


def create_factor(
    state: RiskFactorState,
    *,
    required: bool = True,
) -> RiskFactorResult:
    return RiskFactorResult(
        factor="TEST_FACTOR",
        state=state,
        actual_value=None,
        expected=None,
        explanation="Test factor.",
        required=required,
    )


def test_empty_factors_are_insufficient_data():
    policy = RiskPolicy()

    status = policy.determine_status(())

    assert status == RiskStatus.INSUFFICIENT_DATA


def test_required_missing_factor_is_insufficient_data():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.MISSING),
    )

    status = policy.determine_status(factors)

    assert status == RiskStatus.INSUFFICIENT_DATA


def test_optional_missing_factor_makes_result_limited():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(
            RiskFactorState.MISSING,
            required=False,
        ),
    )

    status = policy.determine_status(factors)

    assert status == RiskStatus.LIMITED


def test_no_missing_factors_are_calculated():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
    )

    status = policy.determine_status(factors)

    assert status == RiskStatus.CALCULATED


def test_insufficient_data_has_no_risk_level():
    policy = RiskPolicy()

    level = policy.determine_level(
        (
            create_factor(RiskFactorState.MISSING),
        ),
        RiskStatus.INSUFFICIENT_DATA,
    )

    assert level is None


def test_error_has_no_risk_level():
    policy = RiskPolicy()

    level = policy.determine_level(
        (
            create_factor(RiskFactorState.MATCHED),
        ),
        RiskStatus.ERROR,
    )

    assert level is None


def test_all_not_matched_results_in_low_risk():
    policy = RiskPolicy()

    factors = tuple(
        create_factor(RiskFactorState.NOT_MATCHED)
        for _ in range(4)
    )

    level = policy.determine_level(
        factors,
        RiskStatus.CALCULATED,
    )

    assert level == RiskLevel.LOW


def test_one_of_four_matched_results_in_moderate_risk():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
    )

    level = policy.determine_level(
        factors,
        RiskStatus.CALCULATED,
    )

    assert level == RiskLevel.MODERATE


def test_two_of_four_matched_results_in_elevated_risk():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
    )

    level = policy.determine_level(
        factors,
        RiskStatus.CALCULATED,
    )

    assert level == RiskLevel.ELEVATED


def test_three_of_four_matched_results_in_high_risk():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.NOT_MATCHED),
    )

    level = policy.determine_level(
        factors,
        RiskStatus.CALCULATED,
    )

    assert level == RiskLevel.HIGH


def test_all_matched_results_in_high_risk():
    policy = RiskPolicy()

    factors = tuple(
        create_factor(RiskFactorState.MATCHED)
        for _ in range(4)
    )

    level = policy.determine_level(
        factors,
        RiskStatus.CALCULATED,
    )

    assert level == RiskLevel.HIGH


def test_missing_optional_factor_is_excluded_from_ratio():
    policy = RiskPolicy()

    factors = (
        create_factor(RiskFactorState.MATCHED),
        create_factor(RiskFactorState.MATCHED),
        create_factor(
            RiskFactorState.MISSING,
            required=False,
        ),
    )

    status = policy.determine_status(factors)
    level = policy.determine_level(factors, status)

    assert status == RiskStatus.LIMITED
    assert level == RiskLevel.HIGH


@pytest.mark.parametrize(
    ("ratio", "expected_level"),
    [
        (0.0, RiskLevel.LOW),
        (0.249, RiskLevel.LOW),
        (0.25, RiskLevel.MODERATE),
        (0.499, RiskLevel.MODERATE),
        (0.50, RiskLevel.ELEVATED),
        (0.749, RiskLevel.ELEVATED),
        (0.75, RiskLevel.HIGH),
        (1.0, RiskLevel.HIGH),
    ],
)
def test_risk_level_boundaries(
    ratio,
    expected_level,
):
    policy = RiskPolicy()

    assert policy._level_from_ratio(ratio) == expected_level