from flask import Blueprint, render_template

from app.services import ThreatService


threat_web = Blueprint(
    "threat_web",
    __name__,
)


@threat_web.get("/threats")
def get_threat_catalog():
    service = ThreatService()
    threats = service.get_all_threats()

    return render_template(
        "threats.html",
        threats=threats,
    )