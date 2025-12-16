import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from resources.schemas import StoreSchema

blp = Blueprint("Stores", __name__, description="Store API")


@blp.route("/store/<string:store_id>")
class Stores(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="Store not found")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return "store deleted."
        except KeyError:
            abort(404, message="store not found")


@blp.route("/store/")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return stores.values()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):

        # commenting this as validation will be handled by marshmallow
        # store_data = request.get_json()
        # if "name" not in store_data:
        #     abort(400, message="Bad request, store name missing in data json.")

        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400, message="Store already exist.")
        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store
        return store
