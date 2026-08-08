from app.domain import (
    RiskFactorState,
    RiskLevel,
    RiskStatus,
    UserProfile,
)


def test_user_profile_values():
    assert set(UserProfile) == {
        UserProfile.HUMAN,
        UserProfile.GARDEN,
        UserProfile.VEGETABLE_GARDEN,
    }


def test_risk_level_values():
    assert set(RiskLevel) == {
        RiskLevel.LOW,
        RiskLevel.MODERATE,
        RiskLevel.ELEVATED,
        RiskLevel.HIGH,
    }


def test_risk_status_values():
    assert set(RiskStatus) == {
        RiskStatus.CALCULATED,
        RiskStatus.LIMITED,
        RiskStatus.INSUFFICIENT_DATA,
        RiskStatus.ERROR,
    }


def test_risk_factor_state_values():
    assert set(RiskFactorState) == {
        RiskFactorState.MATCHED,
        RiskFactorState.NOT_MATCHED,
        RiskFactorState.MISSING,
    }