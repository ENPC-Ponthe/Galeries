from flask import Blueprint
from flask_login import login_required
from flask_restplus import Api

resources_api = Blueprint('api.resources', __name__)

@resources_api.before_request     # login nécessaire pour tout le blueprint
@login_required
def before_request():
    pass

api = Api(resources_api)

from . import routes
