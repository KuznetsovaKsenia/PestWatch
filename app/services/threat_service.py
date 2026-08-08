from app.domain import Threat, ThreatDetails
from app.repositories import ThreatRepository


class ThreatService:
    def __init__(
        self,
        repository: ThreatRepository | None = None,
    ):
        self._repository = repository or ThreatRepository()

    def get_all_threats(self) -> list[Threat]:
        return self._repository.get_all()

    def get_threat_by_code(
        self,
        code: str,
    ) -> ThreatDetails | None:
        return self._repository.get_details_by_code(code)