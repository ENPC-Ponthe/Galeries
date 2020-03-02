from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_restplus import Api

private_api = Blueprint('api.private', __name__)

@private_api.before_request     # login nécessaire pour tout le blueprint
@jwt_required
def before_request():
    pass

api = Api(private_api)

from . import routes, reaction_routes, messages_routes
