from db import db


class TagItemModel(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))

    # tag = db.relationship("TagModel", back_populates="tags")
    # items = db.relationship("ItemModel", back_populates="items")
