from flask import Blueprint

# api = Blueprint('api', __name__)
#
# from . import routes
from flask_restplus import Api

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

from .test import *
