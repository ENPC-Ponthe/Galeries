from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restplus import Api

from ... import app

private_api = Blueprint('api.private', __name__)

@private_api.before_request     # login nécessaire pour tout le blueprint
@jwt_required
def before_request():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

api = Api(private_api)

from . import routes, reaction_routes, messages_routes, video_routes, members_routes, user_routes
