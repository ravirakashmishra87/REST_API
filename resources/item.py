import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import ItemModel
from resources.schemas import ItemSchema, ItemUpdateSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Items", __name__, description="Item API")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted."}
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the item.")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):

        # commenting this as it is now handled by marshmallow
        # item_data = request.get_json()
        # if "name" not in item_data or "price" not in item_data:
        #     abort(
        #         400, message="Bad request, name or price missing in request data json."
        #     )

        # item = items[item_id]
        # try:
        #     item |= item_data
        #     return item
        # except KeyError:
        #     abort(404, "Item not found.")

        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemView(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):

        # commenting this as it is now handled by marshmallow
        # item_data = request.get_json()
        # if (
        #     "price" not in item_data
        #     or "name" not in item_data
        #     or "store_id" not in item_data
        # ):
        #     abort(
        #         400,
        #         message="Bad request, ensure name, price and store_id to be included to json data",
        #     )

        # for item in items.values():
        #     if (
        #         item_data["name"] == item["name"]
        #         and item_data["store_id"] == item["store_id"]
        #     ):
        #         abort(400, message="Item already exist.")

        # if item_data["store_id"] not in stores:
        #     abort(404, message="Store not exist")

        # item_id = uuid.uuid4().hex
        # item = {**item_data, "id": item_id}
        # items[item_id] = item

        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting item.")

        return item
