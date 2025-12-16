import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from resources.schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Item API")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return {"items": items[item_id]}
        except KeyError:
            abort(404, message="item not exist")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(404, message="item not found")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):

        # commenting this as it is now handled by marshmallow
        # item_data = request.get_json()
        # if "name" not in item_data or "price" not in item_data:
        #     abort(
        #         400, message="Bad request, name or price missing in request data json."
        #     )

        item = items[item_id]
        try:
            item |= item_data
            return item
        except KeyError:
            abort(404, "Item not found.")


@blp.route("/item")
class ItemView(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return items.values()

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

        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message="Item already exist.")

        if item_data["store_id"] not in stores:
            abort(404, message="Store not exist")

        item_id = uuid.uuid4().hex
        item = {**item_data, "id": item_id}
        items[item_id] = item
        return item
