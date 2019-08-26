from flask_jwt_extended import current_user

from . import api
from flask_restplus import Resource
from ...dao import EventDAO, GalleryDAO, FileDAO
from ...services import EventService, YearService, GalleryService, FileService, CategoryService
from flask import request
import random
import base64
from PIL import Image


@api.route('/create-event')
@api.doc(params=    {
                        'name': 'Example : WEI',
                        'category_slug': '',
                        'event_description': ''
                    })
class CreateEvent(Resource):
    @api.response(201, 'Success - Event created')
    @api.response(401, 'Request incorrect - Missing required parameter')
    @api.response(403, 'Not authorized - account not valid')
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
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        ''' Create a new year'''
        year_value = request.json.get('value')
        year_description = request.json.get('description')

        if not year_value:
            return {
                "title": "Erreur - Impossible de créer l'année",
                "body": "Veuillez renseigner une valeur pour l'année."
            }, 401

        try:
            YearService.create(year_value, year_description, current_user)
        except Exception:
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
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Create a new category'''
        category_value = request.json.get('value')
        category_description = request.json.get('description')

        if not category_value:
            return {
                "title": "Erreur - Impossible de créer la categorie",
                "body": "Veuillez renseigner une valeur pour la categorie."
            }, 401

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
    @api.response(200, 'Success - All moderations done')
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
                except Exception:
                    galeries_failed_to_delete.append(gallery_slug)
                    error = True

        if galeries_to_approve:
            for gallery_slug in galeries_to_approve:
                try:
                    GalleryService.approve(gallery_slug, current_user)
                except Exception:
                    galeries_failed_to_approve.append(gallery_slug)
                    error = True

        if files_to_delete:
            for file_slug in files_to_delete:
                try:
                    FileService.delete(file_slug)
                except Exception:
                    files_failed_to_delete.append(file_slug)
                    error = True

        if files_to_approve:
            for file_slug in files_to_approve:
                try:
                    FileService.approve_by_slug(file_slug)
                except Exception:
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
    @api.response(201, 'Success - Event deleted')
    @api.response(401, 'Request incorrect - Error while deleting')
    @api.response(403, 'Not authorized - account not valid')
    def delete(self, event_slug: str):
        '''Delete the given event'''
        event_dao = EventDAO()

        try:
            event_dao.delete_detaching_galleries(event_slug)
        except Exception:
            return {
                "title": "Erreur - Impossible de supprimer l'événement",
                "body": "Erreur lors de la suppresion"
            }, 401
        return {
            "msg": "Événement supprimé"
        }, 201


@api.route('/get-private-galleries')
class GetPrivateGalleries(Resource):
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        '''Get the list of public galleries of all years'''
        gallery_list = []
        private_galleries = GalleryDAO().find_private()
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

@api.route('/files/not-moderated')
class GetFilesToModerate(Resource):
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        '''get the slug of the files waiting for moderation'''
        files = FileDAO().find_all()

        list_of_files = list(filter(lambda file: file.pending, files))
        encoded_list_of_files = []
        list_of_dim = []
        list_of_slugs = []
        for file in list_of_files:
            encoded = file.base64encodingThumb()
            encoded_list_of_files.append(encoded)
            im = Image.open("/app/ponthe/data/galleries/" + file.file_path)
            width, height = im.size
            list_of_dim.append({"width": width, "height": height})
            list_of_slugs.append(file.slug)

        unaproved_files = []
        for i in range(len(list_of_files)):
            unaproved_files.append({
                "slug": list_of_slugs[i],
                "file_path": list_of_files[i].file_path,
                "base64": encoded_list_of_files[i],
                "full_dimension": list_of_dim[i]
            })

        return  {
                    "unaproved_files": unaproved_files
                }, 200

@api.route('/galleries/not-moderated')
class GetGaleriesToModerate(Resource):
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        '''get the slug of the files waiting for moderation'''
        galleries = GalleryDAO().find_private()
        list_of_slugs = []
        for gallery in galleries:
            list_of_slugs.append(gallery.slug)

        return  {
                    "unaproved_galeries": list_of_slugs
                }, 200


@api.route('/galleries/<gallery_slug>')
class Gallery(Resource):
    @api.response(403, 'Not authorized - account not valid')
    def delete(self, gallery_slug: str):
        try:
            GalleryService.delete(gallery_slug, current_user)
            return {}, 200
        except:
            return {'msg': 'Gallery does not exist'}, 404


@api.route('/galleries/makeprivate')
@api.doc(params=    {
                        'gallery_slugs': 'List of slugs of the galleries to be set private'
                    })
class MakeGalleryPublic(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Turn the given galeries private'''
        ListOfGallerySlugs = request.json.get('gallery_slugs')
        ListOfGalleryFailedToMakePublic = []
        for gallery_slug in ListOfGallerySlugs:
            try:
                GalleryService.make_private(gallery_slug, current_user)
            except:
                ListOfGalleryFailedToMakePublic.append(gallery_slug)
        if len(ListOfGalleryFailedToMakePublic)!=0:
            response = {
                            "msg": "Error failed to make galleries private",
                            "failed_with": ListOfGalleryFailedToMakePublic
                        }
            return response, 400
        response = {"msg": "success"}
        return response, 200


@api.route('/galleries/makepublic')
@api.doc(params=    {
                        'gallery_slugs': 'List of slugs of the galleries to be set public'
                    })
class MakeGalleryPublic(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Turn the given galleries public'''
        ListOfGallerySlugs = request.json.get('gallery_slugs')
        ListOfGalleryFailedToMakePublic = []
        for gallery_slug in ListOfGallerySlugs:
            try:
                GalleryService.make_public(gallery_slug, current_user)
            except:
                ListOfGalleryFailedToMakePublic.append(gallery_slug)
        if len(ListOfGalleryFailedToMakePublic)!=0:
            response = {
                            "msg": "Error failed to make galleries public",
                            "failed_with": ListOfGalleryFailedToMakePublic
                        }
            return response, 400
        response = {"msg": "success"}
        return response, 200
