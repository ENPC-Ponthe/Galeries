from flask import Blueprint
from flask_restplus import Api

public_api = Blueprint('api.public', __name__)
api = Api(public_api)

from . import routes
