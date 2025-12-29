from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import ItemModel
from resources.schemas import ItemSchema, ItemUpdateSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("Items", __name__, description="Item API")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @blp.alt_response(404, description="Item not found.")
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin previlege is required")
        try:
            item = ItemModel.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted."}, 200
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
            item.description = item_data["description"]
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

    @jwt_required()
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
