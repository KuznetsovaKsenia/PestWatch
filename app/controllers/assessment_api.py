from collections.abc import Callable
from datetime import date

from flask import Blueprint, jsonify, request

from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    Location,
    RiskFactorResult,
    RiskResult,
    UserProfile,
)
from app.domain.assessment_summary import AssessmentSummary
from app.integrations.geocoding import GeocodingIntegrationError
from app.services import (
    AssessmentExecutionService,
    AssessmentHistoryService,
    LocationNotFoundError,
    LocationService,
)


def _serialize_location(
    location: Location,
) -> dict:
    return {
        "name": location.name,
        "region": location.region,
        "country": location.country,
        "latitude": location.latitude,
        "longitude": location.longitude,
    }


def _serialize_risk_factor(
    factor: RiskFactorResult,
) -> dict:
    return {
        "factor": factor.factor,
        "state": factor.state.value,
        "actual_value": factor.actual_value,
        "expected": factor.expected,
        "explanation": factor.explanation,
        "required": factor.required,
    }


def _serialize_risk_result(
    result: RiskResult,
) -> dict:
    explanation = result.explanation

    if result.status.value == "ERROR":
        explanation = (
            "Risk assessment could not be completed "
            "because required environmental data "
            "is temporarily unavailable."
        )

    return {
        "threat_code": result.threat_code,
        "status": result.status.value,
        "risk_level": (
            result.risk_level.value
            if result.risk_level is not None
            else None
        ),
        "factors": [
            _serialize_risk_factor(factor)
            for factor in result.factors
        ],
        "explanation": explanation,
    }


def _serialize_observation(
    observation,
) -> dict:
    return {
        "date": observation.date.isoformat(),
        "mean_temperature": (
            observation.mean_temperature
        ),
    }


def _serialize_snapshot(
    snapshot: AssessmentInputSnapshot,
) -> dict:
    weather = snapshot.current_weather
    soil_estimate = (
        snapshot.soil_temperature_10cm_estimate
    )
    degree_days = snapshot.degree_days_10c
    observations = snapshot.historical_observations

    return {
        "current_weather": (
            {
                "observed_at": (
                    weather.observed_at.isoformat()
                ),
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "precipitation": weather.precipitation,
                "wind_speed": weather.wind_speed,
                "soil_temperature": (
                    weather.soil_temperature
                ),
                "soil_temperature_6cm": (
                    weather.soil_temperature_6cm
                ),
                "soil_temperature_18cm": (
                    weather.soil_temperature_18cm
                ),
            }
            if weather is not None
            else None
        ),
        "soil_temperature_10cm_estimate": (
            {
                "depth_cm": soil_estimate.depth_cm,
                "temperature": (
                    soil_estimate.temperature
                ),
                "source_depths_cm": list(
                    soil_estimate.source_depths_cm
                ),
                "source_temperatures": list(
                    soil_estimate.source_temperatures
                ),
                "method": soil_estimate.method.value,
            }
            if soil_estimate is not None
            else None
        ),
        "degree_days_10c": (
            {
                "base_temperature": (
                    degree_days.base_temperature
                ),
                "total": degree_days.total,
                "period_start": (
                    degree_days.period_start.isoformat()
                ),
                "period_end": (
                    degree_days.period_end.isoformat()
                ),
                "observations": [
                    _serialize_observation(observation)
                    for observation
                    in degree_days.observations
                ],
                "method": degree_days.method.value,
            }
            if degree_days is not None
            else None
        ),
        "saturation_deficit_mm_hg": (
            snapshot.saturation_deficit_mm_hg
        ),
        "historical_observations": (
            [
                _serialize_observation(observation)
                for observation in observations
            ]
            if observations is not None
            else None
        ),
    }


def _serialize_summary(
    summary: AssessmentSummary,
) -> dict:
    return {
        "id": summary.id,
        "created_at": summary.created_at.isoformat(),
        "assessment_date": (
            summary.assessment_date.isoformat()
        ),
        "profile": summary.profile.value,
        "location": _serialize_location(
            summary.location
        ),
    }


def _serialize_assessment(
    assessment: Assessment,
) -> dict:
    return {
        "id": assessment.id,
        "created_at": assessment.created_at.isoformat(),
        "assessment_date": (
            assessment.assessment_date.isoformat()
        ),
        "profile": assessment.profile.value,
        "location": _serialize_location(
            assessment.location
        ),
        "historical_start_date": (
            assessment.historical_start_date.isoformat()
            if assessment.historical_start_date
            is not None
            else None
        ),
        "input_snapshot": _serialize_snapshot(
            assessment.input_snapshot
        ),
        "risk_results": [
            _serialize_risk_result(result)
            for result in assessment.risk_results
        ],
    }


def _error_response(
    *,
    code: str,
    message: str,
    status_code: int,
):
    return (
        jsonify(
            {
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                },
            }
        ),
        status_code,
    )


def _parse_location_input(
    payload: dict,
) -> tuple[str, str, str]:
    location_payload = payload["location"]

    if not isinstance(location_payload, dict):
        raise ValueError(
            "Location must be an object."
        )

    name = location_payload["name"]
    region = location_payload["region"]
    country = location_payload["country"]

    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, region, country)
    ):
        raise ValueError(
            "Location fields must be non-empty strings."
        )

    return (
        name.strip(),
        region.strip(),
        country.strip(),
    )


def create_assessment_api(
    *,
    execution_service: AssessmentExecutionService,
    history_service: AssessmentHistoryService,
    location_service: LocationService,
    assessment_date_provider: Callable[[], date] = date.today,
) -> Blueprint:
    assessment_api = Blueprint(
        "assessment_api",
        __name__,
        url_prefix="/api/assessments",
    )

    @assessment_api.post("")
    def create_assessment():
        payload = request.get_json(
            silent=True
        )

        if not isinstance(payload, dict):
            return _error_response(
                code="INVALID_REQUEST",
                message=(
                    "Request body must be a JSON object."
                ),
                status_code=400,
            )

        try:
            (
                location_name,
                location_region,
                location_country,
            ) = _parse_location_input(payload)

            profile = UserProfile(
                payload["profile"]
            )

        except (KeyError, TypeError, ValueError):
            return _error_response(
                code="INVALID_REQUEST",
                message=(
                    "Request contains invalid assessment input."
                ),
                status_code=400,
            )

        try:
            location = location_service.resolve(
                name=location_name,
                region=location_region,
                country=location_country,
            )
        except LocationNotFoundError:
            return _error_response(
                code="LOCATION_NOT_FOUND",
                message=(
                    "Не удалось найти указанное местоположение."
                ),
                status_code=400,
            )
        except GeocodingIntegrationError:
            return _error_response(
                code="LOCATION_SERVICE_UNAVAILABLE",
                message=(
                    "Не удалось определить местоположение. "
                    "Попробуйте позже."
                ),
                status_code=503,
            )

        assessment = execution_service.execute(
            location=location,
            profile=profile,
            assessment_date=(
                assessment_date_provider()
            ),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": _serialize_assessment(
                        assessment
                    ),
                }
            ),
            201,
        )

    @assessment_api.get("")
    def get_assessments():
        history = history_service.get_history()

        return jsonify(
            {
                "success": True,
                "data": [
                    _serialize_summary(summary)
                    for summary in history
                ],
            }
        )

    @assessment_api.get("/<int:assessment_id>")
    def get_assessment(
        assessment_id: int,
    ):
        assessment = history_service.get_assessment(
            assessment_id
        )

        if assessment is None:
            return _error_response(
                code="ASSESSMENT_NOT_FOUND",
                message="Assessment not found.",
                status_code=404,
            )

        return jsonify(
            {
                "success": True,
                "data": _serialize_assessment(
                    assessment
                ),
            }
        )

    return assessment_api
