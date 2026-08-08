from dataclasses import FrozenInstanceError

import pytest

from app.domain import Recommendation, Source, Threat


def test_threat_can_be_created():
    threat = Threat(
        code="TICK",
        name="Иксодовые клещи",
        category="HUMAN",
        description="Клещи с выраженной сезонной активностью.",
        active=True,
    )

    assert threat.code == "TICK"
    assert threat.name == "Иксодовые клещи"
    assert threat.category == "HUMAN"
    assert threat.description == (
        "Клещи с выраженной сезонной активностью."
    )
    assert threat.active is True


def test_source_can_be_created():
    source = Source(
        id=1,
        title="Профилактика укусов клещей",
        organization="Роспотребнадзор",
        url="https://example.test/source",
        description="Информация о профилактике.",
    )

    assert source.id == 1
    assert source.title == "Профилактика укусов клещей"
    assert source.organization == "Роспотребнадзор"
    assert source.url == "https://example.test/source"
    assert source.description == "Информация о профилактике."


def test_recommendation_can_be_created():
    recommendation = Recommendation(
        id=1,
        threat_code="TICK",
        text="Проводить самоосмотр после прогулки.",
        priority=1,
    )

    assert recommendation.id == 1
    assert recommendation.threat_code == "TICK"
    assert recommendation.text == (
        "Проводить самоосмотр после прогулки."
    )
    assert recommendation.priority == 1


@pytest.mark.parametrize(
    ("factory", "attribute", "new_value"),
    [
        (
            lambda: Threat(
                code="TICK",
                name="Иксодовые клещи",
                category="HUMAN",
                description="Описание",
                active=True,
            ),
            "code",
            "OTHER",
        ),
        (
            lambda: Source(
                id=1,
                title="Источник",
                organization="Организация",
                url="https://example.test",
                description="Описание",
            ),
            "title",
            "Другой источник",
        ),
        (
            lambda: Recommendation(
                id=1,
                threat_code="TICK",
                text="Рекомендация",
                priority=1,
            ),
            "priority",
            2,
        ),
    ],
)
def test_threat_catalog_domain_objects_are_immutable(
    factory,
    attribute,
    new_value,
):
    domain_object = factory()

    with pytest.raises(FrozenInstanceError):
        setattr(domain_object, attribute, new_value)