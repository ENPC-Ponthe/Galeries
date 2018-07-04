from flask import Blueprint

private = Blueprint('private', __name__)

from . import views
