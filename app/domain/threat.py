from dataclasses import dataclass


@dataclass(frozen=True)
class Threat:
    code: str
    name: str
    category: str
    description: str
    active: bool