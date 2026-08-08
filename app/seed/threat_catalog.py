from app import db
from app.models import (
    RecommendationModel,
    SourceModel,
    ThreatModel,
)


THREATS = [
    {
        "code": "TICK",
        "name": "Иксодовые клещи",
        "category": "HUMAN",
        "description": (
            "Клещи, активность которых имеет выраженную сезонность "
            "и зависит в том числе от погодных условий."
        ),
        "active": True,
        "recommendations": [
            {
                "text": (
                    "Использовать светлую закрытую одежду, "
                    "затрудняющую попадание клещей на кожу."
                ),
                "priority": 1,
            },
            {
                "text": (
                    "Регулярно осматривать одежду и открытые участки тела "
                    "во время пребывания на природе."
                ),
                "priority": 2,
            },
            {
                "text": (
                    "После возвращения тщательно осмотреть тело, одежду "
                    "и домашних животных."
                ),
                "priority": 3,
            },
        ],
        "sources": [
            {
                "title": "Клещи и меры профилактики: как защитить себя и близких",
                "organization": (
                    "Управление Роспотребнадзора "
                    "по Рязанской области"
                ),
                "url": (
                    "https://62.rospotrebnadzor.ru/content/"
                    "kleshchi-i-mery-profilaktiki-kak-zashchitit-"
                    "sebya-i-blizkih-1"
                ),
                "description": (
                    "Официальные рекомендации по индивидуальной "
                    "профилактике укусов клещей."
                ),
            }
        ],
    },
    {
        "code": "COLORADO_BEETLE",
        "name": "Колорадский жук",
        "category": "VEGETABLE_GARDEN",
        "description": (
            "Вредитель картофеля и других растений семейства "
            "паслёновых."
        ),
        "active": True,
        "recommendations": [
            {
                "text": (
                    "Регулярно осматривать посадки картофеля "
                    "в период активности вредителя."
                ),
                "priority": 1,
            },
            {
                "text": (
                    "Обращать внимание на появление взрослых жуков, "
                    "яйцекладок и личинок."
                ),
                "priority": 2,
            },
            {
                "text": (
                    "При необходимости защитных обработок использовать "
                    "только разрешённые средства и соблюдать регламент "
                    "их применения."
                ),
                "priority": 3,
            },
        ],
        "sources": [
            {
                "title": (
                    "Сигнализационное сообщение № 8 от 5 июня 2026 г. "
                    "Колорадский жук"
                ),
                "organization": "ФГБУ «Россельхозцентр»",
                "url": (
                    "https://rosselhoscenter.ru/ob-uchrezhdenii/filialy/"
                    "severo-zapadnyy/kaliningradskaya-oblast/"
                    "signalizatsionnoe-soobshchenie-8-ot-5-iyunya-"
                    "2026-g-koloradskiy-zhuk/"
                ),
                "description": (
                    "Официальное сообщение о сезонной активности "
                    "колорадского жука и наблюдении за посадками картофеля."
                ),
            }
        ],
    },
    {
        "code": "CABBAGE_APHID",
        "name": "Капустная тля",
        "category": "VEGETABLE_GARDEN",
        "description": (
            "Вредитель капустных культур, активность которого "
            "зависит от температуры и влажности."
        ),
        "active": True,
        "recommendations": [
            {
                "text": (
                    "Регулярно осматривать растения и обращать внимание "
                    "на скопления тли."
                ),
                "priority": 1,
            },
            {
                "text": (
                    "Контролировать состояние листьев, цветоносов "
                    "и молодых частей растений."
                ),
                "priority": 2,
            },
            {
                "text": (
                    "При обнаружении вредителя учитывать рекомендации "
                    "специалистов по защите растений."
                ),
                "priority": 3,
            },
        ],
        "sources": [
            {
                "title": (
                    "Информационный листок №12 от 22.05.2025 г. "
                    "Капустная тля"
                ),
                "organization": "ФГБУ «Россельхозцентр»",
                "url": (
                    "https://rosselhoscenter.ru/ob-uchrezhdenii/filialy/"
                    "tsentralnyy-okrug/orlovskaya-oblast/"
                    "informatsionnyy-listok-12-kapustnaya-tlya/"
                ),
                "description": (
                    "Материал о вредоносности капустной тли "
                    "и благоприятных погодных условиях её развития."
                ),
            }
        ],
    },
    {
        "code": "CODLING_MOTH",
        "name": "Яблонная плодожорка",
        "category": "GARDEN",
        "description": (
            "Распространённый вредитель плодовых культур, "
            "в первую очередь яблони."
        ),
        "active": True,
        "recommendations": [
            {
                "text": (
                    "Регулярно осматривать плодовые деревья "
                    "в период сезонной активности вредителя."
                ),
                "priority": 1,
            },
            {
                "text": (
                    "Следить за сообщениями о начале лёта бабочек "
                    "и появлении гусениц."
                ),
                "priority": 2,
            },
            {
                "text": (
                    "При выборе мер защиты учитывать сроки развития "
                    "вредителя и рекомендации специалистов."
                ),
                "priority": 3,
            },
        ],
        "sources": [
            {
                "title": (
                    "Сигнализационное сообщение от 19.06.2026 г. "
                    "Яблонная плодожорка"
                ),
                "organization": "ФГБУ «Россельхозцентр»",
                "url": (
                    "https://rosselhoscenter.ru/ob-uchrezhdenii/filialy/"
                    "yuzhnyy/astrakhanskaya-oblast/"
                    "signalizatsionnoe-soobshchenie-ot-19-06-2026-g-"
                    "yablonnaya-plodozhorka/"
                ),
                "description": (
                    "Официальное сигнализационное сообщение "
                    "о сезонном развитии яблонной плодожорки."
                ),
            }
        ],
    },
]


def seed_threat_catalog() -> None:
    for threat_data in THREATS:
        threat = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == threat_data["code"]
            )
        ).scalar_one_or_none()

        if threat is not None:
            continue

        threat = ThreatModel(
            code=threat_data["code"],
            name=threat_data["name"],
            category=threat_data["category"],
            description=threat_data["description"],
            active=threat_data["active"],
        )

        for recommendation_data in threat_data["recommendations"]:
            threat.recommendations.append(
                RecommendationModel(
                    text=recommendation_data["text"],
                    priority=recommendation_data["priority"],
                )
            )

        for source_data in threat_data["sources"]:
            source = _get_or_create_source(source_data)
            threat.sources.append(source)

        db.session.add(threat)

    db.session.commit()


def _get_or_create_source(source_data: dict) -> SourceModel:
    source = db.session.execute(
        db.select(SourceModel).where(
            SourceModel.url == source_data["url"]
        )
    ).scalar_one_or_none()

    if source is not None:
        return source

    source = SourceModel(
        title=source_data["title"],
        organization=source_data["organization"],
        url=source_data["url"],
        description=source_data["description"],
    )

    db.session.add(source)

    return source