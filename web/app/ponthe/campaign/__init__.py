from flask import Blueprint

campaign = Blueprint('campaign', __name__)

from . import routes
