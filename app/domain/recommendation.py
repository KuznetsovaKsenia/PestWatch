from dataclasses import dataclass


@dataclass(frozen=True)
class Recommendation:
    id: int
    threat_code: str
    text: str
    priority: int