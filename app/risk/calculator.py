from abc import ABC, abstractmethod

from app.domain import RiskContext, RiskFactorResult


class RiskCalculator(ABC):
    @abstractmethod
    def evaluate(
        self,
        context: RiskContext,
    ) -> tuple[RiskFactorResult, ...]:
        raise NotImplementedError