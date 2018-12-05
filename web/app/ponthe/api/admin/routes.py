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
from ...services import UserService, EventService, YearService
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

@api.route('/create-year')
class CreateYear(Resource):
    @jwt_required
    def post(self):
        year_value = request.json.get('value')
        year_description = request.json.get('description')

        if not year_value:
            return {
                "title": "Erreur - Impossible de créer l'année",
                "body": "Veuillez renseigner une valeur pour l'année."
            }, 401

        current_user = UserDAO.get_by_id(get_jwt_identity())

        try:
            YearService.create(year_value, year_description, current_user)
        except Exception as e:
            return {
                "title": "Erreur - Impossible de créer l'année",
                "body": "Une erreur est survenue lors de la création de l'année'."
            }, 401

        return {
            "msg": "Année créée"
        }, 201
