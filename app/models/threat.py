from app import db


threat_source = db.Table(
    "threat_source",
    db.Column(
        "threat_id",
        db.Integer,
        db.ForeignKey("threats.id"),
        primary_key=True,
    ),
    db.Column(
        "source_id",
        db.Integer,
        db.ForeignKey("sources.id"),
        primary_key=True,
    ),
)


class ThreatModel(db.Model):
    __tablename__ = "threats"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    recommendations = db.relationship(
        "RecommendationModel",
        back_populates="threat",
        cascade="all, delete-orphan",
        order_by="RecommendationModel.priority",
    )

    sources = db.relationship(
        "SourceModel",
        secondary=threat_source,
        back_populates="threats",
    )