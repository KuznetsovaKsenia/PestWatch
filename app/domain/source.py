from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    id: int
    title: str
    organization: str
    url: str
    description: str