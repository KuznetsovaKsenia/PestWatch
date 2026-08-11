from app import db
from app.domain import (
    Recommendation,
    Source,
    Threat,
    ThreatDetails,
)
from app.models import ThreatModel


class ThreatRepository:
    def get_all(self) -> list[Threat]:
        models = db.session.execute(
            db.select(ThreatModel).order_by(ThreatModel.name)
        ).scalars().all()

        return [
            self._to_domain(model)
            for model in models
        ]

    def get_by_code(self, code: str) -> Threat | None:
        model = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == code
            )
        ).scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    def get_details_by_code(
        self,
        code: str,
    ) -> ThreatDetails | None:
        model = db.session.execute(
            db.select(ThreatModel).where(
                ThreatModel.code == code
            )
        ).scalar_one_or_none()

        if model is None:
            return None

        recommendations = tuple(
            Recommendation(
                id=recommendation.id,
                threat_code=model.code,
                text=recommendation.text,
                priority=recommendation.priority,
            )
            for recommendation in model.recommendations
        )

        sources = tuple(
            Source(
                id=source.id,
                title=source.title,
                organization=source.organization,
                url=source.url,
                description=source.description,
            )
            for source in model.sources
        )

        return ThreatDetails(
            threat=self._to_domain(model),
            recommendations=recommendations,
            sources=sources,
        )

    @staticmethod
    def _to_domain(model: ThreatModel) -> Threat:
        return Threat(
            code=model.code,
            name=model.name,
            category=model.category,
            description=model.description,
            active=model.active,
        )

    def get_by_category(
    self,
    category: str,
    ) -> list[Threat]:
        models = db.session.execute(
            db.select(ThreatModel)
            .where(
                ThreatModel.category == category,
                ThreatModel.active.is_(True),
            )
            .order_by(ThreatModel.name)
        ).scalars().all()

        return [
            self._to_domain(model)
            for model in models
        ]