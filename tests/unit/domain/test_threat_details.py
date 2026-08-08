from app.domain import (
    Recommendation,
    Source,
    Threat,
    ThreatDetails,
)


def test_threat_details_can_be_created():
    threat = Threat(
        code="TICK",
        name="Иксодовые клещи",
        category="HUMAN",
        description="Описание",
        active=True,
    )

    recommendation = Recommendation(
        id=1,
        threat_code="TICK",
        text="Проводить самоосмотр.",
        priority=1,
    )

    source = Source(
        id=1,
        title="Источник",
        organization="Организация",
        url="https://example.test",
        description="Описание",
    )

    details = ThreatDetails(
        threat=threat,
        recommendations=(recommendation,),
        sources=(source,),
    )

    assert details.threat == threat
    assert details.recommendations == (recommendation,)
    assert details.sources == (source,)