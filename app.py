import os
import secrets
from flask import Flask, jsonify

# from flask_migrate import Migrate
from flask_smorest import Api
from resources.store import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_jwt_extended import JWTManager
from models import BlocklistModel, UserModel
from db import db
import models


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTION"] = True
    app.config["API_TITLE"] = "FLASK REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
    app.config["JWT_SECRET_KEY"] = "a-string-secret-at-least-256-bits-long"
    db.init_app(app)
    # migrate = Migrate(app, db)

    api = Api(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_in_blocklist(jwt_header, jwt_payload):
        # return jwt_payload["jti"] in BLOCKLIST
        blockedtoken = BlocklistModel.query.filter(
            BlocklistModel.access_token == jwt_payload["jti"]
        ).first()
        return blockedtoken

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"description": "token is revoked", "error": "token_revoked"}),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # check for user type in database
        user = UserModel.query.get(identity)
        if user and user.type == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "Token has expired", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return (
            jsonify(
                {
                    "message": f"Signature verification fail- {error}",
                    "error": "invalid_token",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app
