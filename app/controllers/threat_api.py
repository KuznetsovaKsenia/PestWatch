from flask import Blueprint, jsonify

from app.domain import Threat, ThreatDetails
from app.services import ThreatService


threat_api = Blueprint(
    "threat_api",
    __name__,
    url_prefix="/api/threats",
)


def _serialize_threat(threat: Threat) -> dict:
    return {
        "code": threat.code,
        "name": threat.name,
        "category": threat.category,
        "description": threat.description,
        "active": threat.active,
    }


def _serialize_threat_details(details: ThreatDetails) -> dict:
    return {
        **_serialize_threat(details.threat),
        "recommendations": [
            {
                "text": recommendation.text,
                "priority": recommendation.priority,
            }
            for recommendation in details.recommendations
        ],
        "sources": [
            {
                "title": source.title,
                "organization": source.organization,
                "url": source.url,
                "description": source.description,
            }
            for source in details.sources
        ],
    }


@threat_api.get("")
def get_threats():
    service = ThreatService()
    threats = service.get_all_threats()

    return jsonify(
        {
            "success": True,
            "data": [
                _serialize_threat(threat)
                for threat in threats
            ],
        }
    )


@threat_api.get("/<string:code>")
def get_threat(code: str):
    service = ThreatService()
    details = service.get_threat_by_code(code)

    if details is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "code": "THREAT_NOT_FOUND",
                        "message": "Threat not found.",
                    },
                }
            ),
            404,
        )

    return jsonify(
        {
            "success": True,
            "data": _serialize_threat_details(details),
        }
    )