from collections.abc import Mapping

from app.demo import (
    DemoHistoricalWeatherService,
    DemoScenarioRegistry,
    DemoWeatherService,
)
from app.integrations.geocoding import (
    OpenMeteoGeocodingAdapter,
    OpenMeteoGeocodingClient,
)
from app.integrations.weather import (
    HistoricalWeatherAdapter,
    HistoricalWeatherClient,
    WeatherAdapter,
    WeatherClient,
)
from app.repositories import AssessmentRepository
from app.risk import (
    CodlingMothSeasonStartDetector,
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
    LocationService,
    RiskAssessmentOrchestrator,
    ThreatService,
    WeatherService,
)
from app.weather import (
    DegreeDaysCalculator,
    SaturationDeficitCalculator,
    SoilTemperatureEstimator,
)


def build_assessment_services(
    config: Mapping,
) -> tuple[
    AssessmentExecutionService,
    AssessmentHistoryService,
    LocationService,
]:
    repository = AssessmentRepository()

    assessment_service = AssessmentService(repository)
    history_service = AssessmentHistoryService(repository)

    location_service = LocationService(
        client=OpenMeteoGeocodingClient(
            base_url=config["GEOCODING_API_BASE_URL"],
            timeout_seconds=config["GEOCODING_API_TIMEOUT_SECONDS"],
        ),
        adapter=OpenMeteoGeocodingAdapter(),
    )

    input_requirements = RiskInputRequirements()

    context_preparer = RiskContextPreparer(
        requirements=input_requirements,
        soil_temperature_estimator=SoilTemperatureEstimator(),
        degree_days_calculator=DegreeDaysCalculator(),
        saturation_deficit_calculator=SaturationDeficitCalculator(),
    )

    calculator_registry = RiskCalculatorRegistry(
        {
            "TICK": TickRiskCalculator(),
            "CABBAGE_APHID": CabbageAphidRiskCalculator(),
            "COLORADO_BEETLE": ColoradoBeetleRiskCalculator(),
            "CODLING_MOTH": CodlingMothRiskCalculator(),
        }
    )

    evaluator = SingleThreatRiskEvaluator(
        context_preparer=context_preparer,
        calculator_registry=calculator_registry,
        engine=RiskEngine(RiskPolicy()),
    )

    weather_service = WeatherService(
        client=WeatherClient(
            base_url=config["WEATHER_API_BASE_URL"],
            timeout_seconds=config["WEATHER_API_TIMEOUT_SECONDS"],
        ),
        adapter=WeatherAdapter(),
    )

    historical_weather_service = HistoricalWeatherService(
        client=HistoricalWeatherClient(
            base_url=config["WEATHER_ARCHIVE_API_BASE_URL"],
            timeout_seconds=config["WEATHER_ARCHIVE_API_TIMEOUT_SECONDS"],
        ),
        adapter=HistoricalWeatherAdapter(),
    )

    season_start_detector = CodlingMothSeasonStartDetector()

    orchestrator = RiskAssessmentOrchestrator(
        threat_service=ThreatService(),
        weather_service=weather_service,
        historical_weather_service=historical_weather_service,
        input_requirements=input_requirements,
        evaluator=evaluator,
        season_start_detector=season_start_detector,
    )

    demo_scenario_registry = DemoScenarioRegistry()

    demo_orchestrator = RiskAssessmentOrchestrator(
        threat_service=ThreatService(),
        weather_service=DemoWeatherService(demo_scenario_registry),
        historical_weather_service=DemoHistoricalWeatherService(
            demo_scenario_registry
        ),
        input_requirements=input_requirements,
        evaluator=evaluator,
        season_start_detector=season_start_detector,
    )

    execution_service = AssessmentExecutionService(
        orchestrator=orchestrator,
        assessment_service=assessment_service,
        demo_orchestrator=demo_orchestrator,
        demo_scenario_registry=demo_scenario_registry,
    )

    return (
        execution_service,
        history_service,
        location_service,
    )
