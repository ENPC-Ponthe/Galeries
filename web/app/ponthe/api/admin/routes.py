from flask_jwt_extended import JWTManager, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO, EventDAO, CategoryDAO, GalleryDAO
from ...middlewares import admin_only, jwt_check
from ...config import constants
from sqlalchemy.orm.exc import NoResultFound
import re
from ... import db
from ...services import UserService, EventService, YearService, GalleryService, FileService, CategoryService
from flask import request
import random
import base64

@api.route('/create-event')
@api.doc(params=    {
                        'name': 'Example : WEI',
                        'category_slug': '',
                        'event_description': ''
                    })
class CreateEvent(Resource):
    @jwt_check
    @admin_only
    @api.response(201, 'Success - Event created')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(401, 'Request incorrect - Missing required parameter')
    def post(self):
        '''Create a new event'''
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
    @jwt_check
    @admin_only
    def post(self):
        ''' Create a new year'''
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
        }, 201

@api.route('/create-category')
@api.doc(params=    {
                        'name': 'Example : Sport',
                        'description': ''
                    })
class CreateCategory(Resource):
    @jwt_check
    @admin_only
    def post(self):
        '''Create a new category'''
        category_value = request.json.get('value')
        category_description = request.json.get('description')

        if not category_value:
            return {
                "title": "Erreur - Impossible de créer la categorie",
                "body": "Veuillez renseigner une valeur pour la categorie."
            }, 401

        current_user = UserDAO.get_by_id(get_jwt_identity())
        CategoryService.create(category_value, category_description, current_user)

        return {
            "msg": "Catégorie créée"
        }, 201

@api.route('/moderation')
@api.doc(params=    {
                        'galleries_to_delete': 'Liste des slug de galeries à supprimer',
                        'galleries_to_approve': 'Liste des slugs de galeries à approuver',
                        'files_to_delete': 'Liste des slugs de fichiers à supprimer',
                        'files_to_approve': 'Liste des slugs de fichiers à approuver'
                    })
class Moderation(Resource):
    @jwt_check
    @admin_only
    @api.response(200, 'Success - All moderations done')
    # @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(401, 'Request incorrect - Error while moderating')
    def post(self):
        '''Moderate given galeries and files'''
        galeries_to_delete = request.json.get('galleries_to_delete')
        galeries_to_approve = request.json.get('galleries_to_approve')
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
                    GalleryService.delete(gallery_slug, current_user)
                except Exception as e:
                    galeries_failed_to_delete.append(gallery_slug)
                    error = True

        if galeries_to_approve:
            for gallery_slug in galeries_to_approve:
                try:
                    GalleryService.approve(gallery_slug, current_user)
                except Exception as e:
                    galeries_failed_to_approve.append(gallery_slug)
                    error = True

        if files_to_delete:
            for file_slug in files_to_delete:
                try:
                    FileService.delete(file_slug, current_user)
                except Exception as e:
                    files_failed_to_delete.append(file_slug)
                    error = True

        if files_to_approve:
            for file_slug in files_to_approve:
                try:
                    FileService.approve_by_slug(file_slug)
                except Exception as e:
                    files_failed_to_approve.append(file_slug)
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
    @jwt_check
    @admin_only
    @api.response(201, 'Success - Event deleted')
    @api.response(401, 'Request incorrect - Error while deleting')
    def delete(self, event_slug):
        '''Delete the given event'''
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


@api.route('/get-private-galleries')
class GetPrivateGalleries(Resource):
    @jwt_check
    @admin_only
    @api.response(200, 'Success')
    def get(self):
        '''Get the list of public galleries of all years'''
        gallery_list = []
        private_galleries = GalleryDAO().find_all_private()
        for gallery in private_galleries:
            list_of_files = list(filter(lambda file: not file.pending, gallery.files))
            encoded_string = ""
            if(len(list_of_files) > 0):
                i = random.randint(0, len(list_of_files)-1)
                with open("/app/instance/thumbs/" + list_of_files[i].get_thumb_path(), "rb") as image_file:
                    encoded_string = "data:image/"+list_of_files[i].extension+";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
                image_file.close()
            gallery_list.append({
                "name": gallery.name,
                "slug": gallery.slug,
                "image": encoded_string
            })
        data =  {
                    "galleries": gallery_list
                }
        return data, 200
