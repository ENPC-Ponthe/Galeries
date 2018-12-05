from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO, EventDAO
from itsdangerous import SignatureExpired, BadSignature
from ...config import constants
from sqlalchemy.orm.exc import NoResultFound
import re
# from urllib.parse import urlparse, urljoin
# from flask_login import login_user, current_user
from itsdangerous import SignatureExpired, BadSignature
from datetime import datetime

# from . import public
from ... import app, db, login_manager
from ...services import UserService, EventService
from flask import request

@api.route('/create-event')
class CreateEvent(Resource):
    @jwt_required
    def post(self):
        name = request.json.get('name')
        category_slug = request.json.get('category_slug')
        event_description = request.json.get('event_description')

        if not name:
            return  {
                "title": "Erreur - Impossible de créer l'événement",
                "body": "Veuillez renseigner un nom pour l'événement."
            }, 401

        current_user = UserDAO.get_by_id(get_jwt_identity())

        EventService.create(name, event_description, category_slug, current_user)

        return {
            "msg": "Événement créé"
        }, 201
