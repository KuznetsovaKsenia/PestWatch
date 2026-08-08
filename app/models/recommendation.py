from app import db


class RecommendationModel(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)

    threat_id = db.Column(
        db.Integer,
        db.ForeignKey("threats.id"),
        nullable=False,
        index=True,
    )

    text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, nullable=False)

    threat = db.relationship(
        "ThreatModel",
        back_populates="recommendations",
    )