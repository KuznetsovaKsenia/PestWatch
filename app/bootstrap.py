from collections.abc import Mapping

from app.integrations.weather import (
    HistoricalWeatherAdapter,
    HistoricalWeatherClient,
    WeatherAdapter,
    WeatherClient,
)
from app.repositories import AssessmentRepository
from app.risk import (
    RiskCalculatorRegistry,
    RiskContextPreparer,
    RiskEngine,
    RiskInputRequirements,
    RiskPolicy,
    SingleThreatRiskEvaluator,
)
from app.risk.calculators import (
    CabbageAphidRiskCalculator,
    CodlingMothRiskCalculator,
    ColoradoBeetleRiskCalculator,
    TickRiskCalculator,
)
from app.services import (
    AssessmentExecutionService,
    AssessmentHistoryService,
    AssessmentService,
    HistoricalWeatherService,
    RiskAssessmentOrchestrator,
    ThreatService,
    WeatherService,
)
from app.weather import (
    DegreeDaysCalculator,
    SoilTemperatureEstimator,
)


def build_assessment_services(
    config: Mapping,
) -> tuple[
    AssessmentExecutionService,
    AssessmentHistoryService,
]:
    repository = AssessmentRepository()

    assessment_service = AssessmentService(
        repository
    )
    history_service = AssessmentHistoryService(
        repository
    )

    input_requirements = RiskInputRequirements()

    context_preparer = RiskContextPreparer(
        requirements=input_requirements,
        soil_temperature_estimator=(
            SoilTemperatureEstimator()
        ),
        degree_days_calculator=(
            DegreeDaysCalculator()
        ),
    )

    calculator_registry = RiskCalculatorRegistry(
        {
            "TICK": TickRiskCalculator(),
            "CABBAGE_APHID": (
                CabbageAphidRiskCalculator()
            ),
            "COLORADO_BEETLE": (
                ColoradoBeetleRiskCalculator()
            ),
            "CODLING_MOTH": (
                CodlingMothRiskCalculator()
            ),
        }
    )

    evaluator = SingleThreatRiskEvaluator(
        context_preparer=context_preparer,
        calculator_registry=calculator_registry,
        engine=RiskEngine(RiskPolicy()),
    )

    weather_service = WeatherService(
        client=WeatherClient(
            base_url=config[
                "WEATHER_API_BASE_URL"
            ],
            timeout_seconds=config[
                "WEATHER_API_TIMEOUT_SECONDS"
            ],
        ),
        adapter=WeatherAdapter(),
    )

    historical_weather_service = (
        HistoricalWeatherService(
            client=HistoricalWeatherClient(
                base_url=config[
                    "WEATHER_ARCHIVE_API_BASE_URL"
                ],
                timeout_seconds=config[
                    "WEATHER_ARCHIVE_API_TIMEOUT_SECONDS"
                ],
            ),
            adapter=HistoricalWeatherAdapter(),
        )
    )

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=ThreatService(),
        weather_service=weather_service,
        historical_weather_service=(
            historical_weather_service
        ),
        input_requirements=input_requirements,
        evaluator=evaluator,
    )

    execution_service = AssessmentExecutionService(
        orchestrator=orchestrator,
        assessment_service=assessment_service,
    )

    return execution_service, history_service