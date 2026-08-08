from app import db


class SourceModel(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.Text, nullable=False)

    threats = db.relationship(
        "ThreatModel",
        secondary="threat_source",
        back_populates="sources",
    )