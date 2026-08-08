import pytest

from app.risk import RiskCalculator


def test_risk_calculator_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        RiskCalculator()