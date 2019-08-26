from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import Api, abort
from http import HTTPStatus

admin_api = Blueprint('api.admin', __name__)

@admin_api.before_request     # login en tant qu'admin nécessaire pour tout le blueprint
@jwt_required
def before_request():
    if not current_user.admin:
        abort(code=HTTPStatus.FORBIDDEN, message="You are not an admin")

api = Api(admin_api)

from . import routes
