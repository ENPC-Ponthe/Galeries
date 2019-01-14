from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO, EventDAO, CategoryDAO
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
from ...services import UserService, EventService, YearService, GalleryService, FileService, CategoryService
from flask import request, jsonify

# @app.before_request     # login en tant qu'admin nécessaire pour tout le blueprint
# def before_request():
#     current_user = UserDAO.get_by_id(get_jwt_identity())
#     if not current_user.admin:
#         return {
#             "title": "Erreur - Impossible de supprimer l'événement",
#             "body": "L'utilisateur n'est pas administrateur"
#         }, 401
#         # abort(401)

@api.route('/create-event')
@api.doc(params=    {
                        'name': 'Example : WEI',
                        'category_slug': '',
                        'event_description': ''
                    })
class CreateEvent(Resource):
    @jwt_required
    @api.response(201, 'Success - Event created')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(401, 'Request incorrect - Missing required parameter')
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
@api.doc(params=    {
                        'value': 'Example : 2018',
                        'description': ''
                    })
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
                "body": "Une erreur est survenue lors de la création de l'année."
            }, 401

        return {
            "msg": "Année créée"
        }, 20
@api.route('/create-category')
@api.doc(params=    {
                        'value': 'Example : Sport',
                        'description': '',
                        'category_slug': ''
                    })
class CreateCategory(Resource):
    @jwt_required
    def post(self):
        category_value = request.json.get('value')
        category_description = request.json.get('description')
        category_slug = request.json.get('category_slug')

        if not category_value:
            return {
                "title": "Erreur - Impossible de créer la categorie",
                "body": "Veuillez renseigner une valeur pour la categorie."
            }, 401

        current_user = UserDAO.get_by_id(get_jwt_identity())
        # try:
        CategoryService.create(category_value, category_description, category_slug, current_user)
        # except Exception as e:
            # return {
            #     "title": "Erreur - Impossible de créer la categorie",
            #     "body": "Une erreur est survenue lors de la création de la categorie."
            # }, 401

        return {
            "msg": "Catégorie créée"
        }, 201

@api.route('/moderation')
@api.doc(params=    {
                        'galeries_to_delete': 'Liste des slug de galeries à supprimer',
                        'galeries_to_approve': 'Liste des slugs de galeries à approuver',
                        'files_to_delete': 'Liste des slugs de fichiers à supprimer',
                        'files_to_approve': 'Liste des slugs de fichiers à approuver'
                    })
class Moderation(Resource):
    @jwt_required
    @api.response(200, 'Success - All moderations done')
    # @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(401, 'Request incorrect - Error while moderating')
    def post(self):
        galeries_to_delete = request.json.get('galeries_to_delete')
        galeries_to_approve = request.json.get('galeries_to_approve')
        files_to_delete = request.json.get('files_to_delete')
        files_to_approve = request.json.get('files_to_approve')

        galeries_failed_to_delete = []
        galeries_failed_to_approve = []
        files_failed_to_delete = []
        files_failed_to_approve = []

        error = False

        if galeries_to_delete:
            for gallery_slug in galeries_to_delete:
                try:
                    GalleryService.delete(gallery_slug)
                except Exception as e:
                    galeries_failed_to_delete.append(gallery_slug)
                    error = True

        if galeries_to_approve:
            for gallery_slug in galeries_to_approve:
                try:
                    GalleryService.delete(gallery_slug)
                except Exception as e:
                    galeries_failed_to_approve.append(gallery_slug)
                    error = True

        if files_to_delete:
            for file_slug in files_to_delete:
                try:
                    FileService.delete(file_slug)
                except Exception as e:
                    files_failed_to_delete.append(files_slug)
                    error = True

        if files_to_approve:
            for file_slug in files_to_approve:
                try:
                    FileService.delete(file_slug)
                except Exception as e:
                    files_failed_to_approve.append(files_slug)
                    error = True

        if error:
            return {
                "title": "Erreur - Impossible de modérer certains éléments",
                "body": "Une erreur est survenue lors de la modération d'un ou plusieurs éléments.",
                "galeries_failed_to_delete": galeries_failed_to_delete,
                "galeries_failed_to_approve": galeries_failed_to_approve,
                "files_failed_to_delete": files_failed_to_delete,
                "files_failed_to_approve": files_failed_to_approve
            }, 401

        return {
            "msg": "Toutes les modérations ont été effectuées."
        }, 200

@api.route('/delete-event/<event_slug>')
class DeleteEvent(Resource):
    @jwt_required
    @api.response(201, 'Success - Event deleted')
    @api.response(401, 'Request incorrect - Error while deleting')
    def delete(self, event_slug):
        event_dao = EventDAO()

        current_user = UserDAO.get_by_id(get_jwt_identity())

        try:
            event_dao.delete_detaching_galleries(event_slug)
        except Exception as e:
            return {
                "title": "Erreur - Impossible de supprimer l'événement",
                "body": "Erreur lors de la suppresion"
            }, 401
        return {
            "msg": "Événement supprimé"
        }, 201
