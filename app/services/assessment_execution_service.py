from datetime import date

from app.demo import DemoScenarioRegistry
from app.domain import Assessment, Location, UserProfile
from app.services.assessment_service import AssessmentService
from app.services.risk_assessment_orchestrator import RiskAssessmentOrchestrator


class DemoModeUnavailableError(RuntimeError):
    """Demo assessment infrastructure is not configured."""


class AssessmentExecutionService:
    def __init__(
        self,
        orchestrator: RiskAssessmentOrchestrator,
        assessment_service: AssessmentService,
        *,
        demo_orchestrator: RiskAssessmentOrchestrator | None = None,
        demo_scenario_registry: DemoScenarioRegistry | None = None,
    ):
        self._orchestrator = orchestrator
        self._assessment_service = assessment_service
        self._demo_orchestrator = demo_orchestrator
        self._demo_scenario_registry = demo_scenario_registry

    def execute(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> Assessment:
        return self._execute_with_orchestrator(
            orchestrator=self._orchestrator,
            location=location,
            profile=profile,
            assessment_date=assessment_date,
            historical_start_date=historical_start_date,
        )

    def execute_demo(
        self,
        *,
        scenario_id: str,
        profile: UserProfile,
    ) -> Assessment:
        if self._demo_orchestrator is None or self._demo_scenario_registry is None:
            raise DemoModeUnavailableError(
                "Demo assessment infrastructure is not configured."
            )

        scenario = self._demo_scenario_registry.get(scenario_id)

        return self._execute_with_orchestrator(
            orchestrator=self._demo_orchestrator,
            location=scenario.location,
            profile=profile,
            assessment_date=scenario.assessment_date,
        )

    def _execute_with_orchestrator(
        self,
        *,
        orchestrator: RiskAssessmentOrchestrator,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> Assessment:
        risk_results, input_snapshot = orchestrator.evaluate_with_snapshot(
            location=location,
            profile=profile,
            assessment_date=assessment_date,
            historical_start_date=historical_start_date,
        )

        resolved_historical_start_date = historical_start_date

        if (
            resolved_historical_start_date is None
            and input_snapshot.degree_days_10c is not None
        ):
            resolved_historical_start_date = (
                input_snapshot.degree_days_10c.period_start
            )

        return self._assessment_service.save_assessment(
            location=location,
            profile=profile,
            assessment_date=assessment_date,
            historical_start_date=resolved_historical_start_date,
            input_snapshot=input_snapshot,
            risk_results=risk_results,
        )
