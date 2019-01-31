from flask import Blueprint
from flask_restplus import Api

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

from .public import routes
from .private import routes
from .admin import routes
from . import test
