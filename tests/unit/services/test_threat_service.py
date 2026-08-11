from unicodedata import category

from app.domain import (
    Recommendation,
    Source,
    Threat,
    ThreatDetails,
    UserProfile,
)

from app.services import ThreatService


class FakeThreatRepository:
    def __init__(self):
        self.received_category = None
        self.threat = Threat(
            code="TICK",
            name="Иксодовые клещи",
            category="HUMAN",
            description="Описание",
            active=True,
        )

        self.details = ThreatDetails(
            threat=self.threat,
            recommendations=(
                Recommendation(
                    id=1,
                    threat_code="TICK",
                    text="Проводить самоосмотр.",
                    priority=1,
                ),
            ),
            sources=(
                Source(
                    id=1,
                    title="Источник",
                    organization="Организация",
                    url="https://example.test",
                    description="Описание",
                ),
            ),
        )

    def get_all(self):
        return [self.threat]

    def get_by_category(self, category):
        self.received_category = category

        if category == "HUMAN":
            return [self.threat]

        return []

    def get_details_by_code(self, code):
        if code == "TICK":
            return self.details

        return None


def test_service_returns_all_threats():
    repository = FakeThreatRepository()
    service = ThreatService(repository)

    threats = service.get_all_threats()

    assert threats == [repository.threat]


def test_service_returns_threat_details_by_code():
    repository = FakeThreatRepository()
    service = ThreatService(repository)

    details = service.get_threat_by_code("TICK")

    assert details == repository.details
    assert details.threat.code == "TICK"


def test_service_returns_none_for_unknown_code():
    service = ThreatService(FakeThreatRepository())

    details = service.get_threat_by_code("UNKNOWN")

    assert details is None

def get_by_category(self, category):
    self.received_category = category

    if category == "HUMAN":
        return [self.threat]

    return []

def test_service_returns_threats_for_profile():
    repository = FakeThreatRepository()
    service = ThreatService(repository)

    threats = service.get_threats_for_profile(
        UserProfile.HUMAN,
    )

    assert threats == [repository.threat]

def test_service_uses_profile_value_as_threat_category():
    repository = FakeThreatRepository()
    service = ThreatService(repository)

    service.get_threats_for_profile(
        UserProfile.HUMAN,
    )

    assert repository.received_category == "HUMAN"