from db import db


class BlocklistModel(db.Model):
    __tablename__ = "blocked_tokens"

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(500), nullable=False)
