from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from flask_mail import Message
from ...persistence import UserDAO, YearDAO, EventDAO, GalleryDAO, FileDAO
from itsdangerous import SignatureExpired, BadSignature
from ...config import constants
from sqlalchemy.orm.exc import NoResultFound
import re
import json
from flask import jsonify, send_file
# from urllib.parse import urlparse, urljoin
# from flask_login import login_user, current_user
from itsdangerous import SignatureExpired, BadSignature
from datetime import datetime
from werkzeug.utils import secure_filename
# from . import public
from ... import app, db, login_manager, mail
from ...services import UserService, GalleryService
from flask import request
# from ...models import serialize
import random
import base64
import os
from ...services import FileService
import time
from ... import thumb
from PIL import Image
import io

UPLOAD_FOLDER = '/app/instance/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
THUMBS_FOLDER = "/app/instance/thumbs/"
# @app.template_filter('thumb')
# def thumb_filter(file):
#     return thumb.get_thumbnail(file.file_path, '226x226')
#
# @app.template_filter('category_thumb')
# def thumb_filter(file):
#     return thumb.get_thumbnail(file.file_path, '630x500')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/file_upload/<gallery_slug>')
@api.doc(params=    {
                        'file': 'file to upload',
                    })
class Upload(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - accound not valid')
    @api.response(401, 'Bad Request')
    def post(self, gallery_slug):
        '''upload a file in a gallery'''
        if 'file' not in request.files:
            return {
                        "msg": "Bad request"
                    }, 401

        file = request.files['file']
        current_user = UserDAO.get_by_id(get_jwt_identity())

        if file and allowed_file(file.filename):
            filename = secure_filename(base64.b64encode(bytes(str(time.time()) + file.filename,'utf-8')).decode('utf-8')+ "." + file.filename.rsplit('.', 1)[1].lower())
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            FileService.create(os.path.join(UPLOAD_FOLDER, filename), filename, gallery_slug, current_user)
            return {
                        "msg": "File has been saved"
                    }, 200


@api.route('/files/not-moderated')
class GetFilesToModerate(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        '''get the slug of the files waiting for moderation'''
        files = FileDAO().find_all()

        NotModeratedFileSlugs = []
        for file in files:
            if file.pending:
                NotModeratedFileSlugs.append(file.slug)
        return  {
                    "unaproved_files": NotModeratedFileSlugs
                }, 200


@api.route('/get_user_by_jwt')
class GetUser(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        current_user = UserDAO.get_by_id(get_jwt_identity())
        return {
                    "firstname": current_user.firstname,
                    "lastname": current_user.lastname,
                    "email": current_user.email
                }, 200

@api.route('/materiel')
@api.doc(params=    {
                        'device': 'object you would like to borrow to the club',
                        'message': 'your message'
                    })
class Materiel(Resource):
    @jwt_required
    @api.response(200, 'Success - Mail sent')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Send a mail to ponthe to borrow material'''
        object = request.json.get('device')
        message = request.json.get('message')
        if not message:
            return  {
                "title": "Erreur - Aucun message",
                "body": "Veuillez saisir un message"
            }, 400
        current_user = UserDAO.get_by_id(get_jwt_identity())
        msg = Message(subject=f"Demande d'emprunt de {object} par {current_user.firstname} {current_user.lastname}",
                      body=message,
                      sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                      recipients=['alexperez3498@hotmail.fr', 'ponthe@liste.enpc.fr'])#['ponthe@liste.enpc.fr'])
        mail.send(msg)
        return  {
            "msg": "Mail envoyé !"
        }, 200

# @private.route('/years/<year_slug>', methods=['GET', 'POST'])
# def year_gallery(year_slug):
#     year_dao = YearDAO()
#     if request.method == 'POST' and "delete" in request.form and current_user.admin:
#         year_dao.delete_detaching_galleries(year_slug)
#         return redirect("/index")
#     try:
#         year = year_dao.find_by_slug(year_slug)
#     except NoResultFound:
#         raise NotFound()
#     public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
#     return render_template('year_gallery.html', year=year, public_galleries=public_galleries)


@api.route('/get-galleries-of-year/<year_slug>')
@api.doc(params=    {
                        'year_slug': 'Example : 2018'
                    })
class Year(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(404, 'Year not found')
    def get(self, year_slug):
        '''Get the list of public galleries of a given year'''
        year_dao = YearDAO()
        year = year_dao.find_by_slug(year_slug)
        try:
            public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
            return {
                "year": year_dao.serialize(year_slug),
                "public_galleries": [gallery.slug for gallery in public_galleries]
            }, 200
        except NoResultFound:
            return {'msg': 'year not found'}, 404

    @jwt_required
    @api.response(200, 'Success')
    @api.response(40, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - not admin')
    def delete(self, year_slug):
        '''Delete a given year'''
        year_dao = YearDAO()
        current_user = UserDao().get_by_id(get_jwt_identity)
        if current_user.admin:
            try:
                 year_dao.delete_detaching_galleries(year_slug)
                 return {'msg': 'year deleted'}, 200
            except NoResultFound:
                 return {'msg': 'year not found'}, 404
        return {'msg': 'not admin'}, 403

@api.route('/get-galleries-by-year')
class GetGalleriesByYear(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(404, 'Year not found')
    def post(self):
        '''Get the list of public galleries of all years'''

        without_base64 = request.json.get('without_base64')

        if without_base64 == None:
            without_base64 = False

        year_dao = YearDAO()
        year_list = year_dao.find_all_ordered_by_value()
        data = []
        for year in year_list:
            public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
            gallery_list = []
            for gallery in public_galleries:
                list_of_files = list(filter(lambda file: not file.pending, gallery.files))
                encoded_string = ""
                if(len(list_of_files) > 0):
                    i = random.randint(0, len(list_of_files)-1)
                    with open("/app/instance/thumbs/" + list_of_files[i].get_thumb_path(), "rb") as image_file:
                        encoded_string = "data:image/"+list_of_files[i].extension+";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
                    image_file.close()
                if without_base64:
                    gallery_list.append({
                        "name": gallery.name,
                        "slug": gallery.slug,
                        "file_path": list_of_files[i].file_path
                    })
                else:
                    gallery_list.append({
                        "name": gallery.name,
                        "slug": gallery.slug,
                        "file_path": list_of_files[i].file_path,
                        "image": encoded_string
                    })
            data.append({
                "year": year.value,
                "galleries": gallery_list
            })
        return {
            "data": data
        }, 200


@api.route('/get-all-galleries')
class GetAllGalleries(Resource):
    @jwt_required
    @api.response(200, 'Success')
    def get(self):
        '''Get the list of public galleries of all years'''
        gallery_list = []
        public_galleries = GalleryDAO().find_all_public()
        for gallery in public_galleries:
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
        # try:
        #     public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
        #     return {
        #         "year": year_dao.serialize(year_slug),
        #         "public_galleries": [gallery.slug for gallery in public_galleries]
        #     }, 200
        # except NoResultFound:
        #     return {'msg': 'year not found'}, 404


@api.route('/create-gallery')
@api.doc(params=    {
                        'name': 'Gallery name',
                        'description': '',
                        'year_slug': 'Slug of the year of the galery. Ex: 2019',
                        'event_slug': 'Slug of the parent event of the galery.',
                        'private': 'Boolean'
                    })
class CreateGallery(Resource):
    @jwt_required
    @api.response(201, 'Success - Gallery created')
    @api.response(401, 'Request incorrect - Error while creating gallery')
    def post(self):
        '''Create a new gallery'''
        gallery_name = request.json.get('name')
        gallery_description = request.json.get('description')
        year_slug = request.json.get('year_slug')
        event_slug = request.json.get('event_slug')
        private = request.json.get('private')

        if not gallery_name:
            return  {
                "title": "Erreur - Paramètre manquant",
                "body": "Veuillez renseigner le nom de la nouvelle galerie"
            }, 401

        current_user = UserDAO.get_by_id(get_jwt_identity())

        try:
            GalleryService.create(gallery_name, current_user, gallery_description, private == "on", year_slug, event_slug)

        except Exception as e:
            return  {
                "title": "Erreur - Impossible de créer la gallerie",
                "body": "Une erreur est survenue lors de la création de la gallerie. Probablement qu'un des objets donné n'existe pas (year ou event). "+str(e)
            }, 401

        return {
            "msg": "Gallerie créée"
        }, 201

@api.route('/members')
class Members(Resource):
    @jwt_required
    def get(self):
        '''Get Ponthe members'''
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        members = open(os.path.join(SITE_ROOT, "/app/ponthe/templates", "members.json"))
        return json.load(members, strict=False)


@api.route('/get-galleries/<event_slug>')
class GetGalleries(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(404, 'No corresponding event to event_slug')
    def get(self, event_slug):
        '''Get the list of galleries of an event'''
        event_dao = EventDAO()

        try:
            event = event_dao.find_by_slug(event_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Impossible de trouver l'événement",
                "body": "Aucun événement ne correspond à : "+event_slug
            }, 404

        galleries_by_year = {}
        other_galleries = []
        for gallery in event.galleries:
            if gallery.private:
                continue
            year = gallery.year
            if year is not None:
                if year not in galleries_by_year:
                    galleries_by_year[year] = []
                galleries_by_year[year].append(gallery)
            else:
                other_galleries.append(gallery)

        # Building json encodable dict and list for response
        gby_dict = dict()
        for year, galleries in galleries_by_year.items():
            gby_dict[year.slug] = [gallery.serialize() for gallery in galleries]

        og_list=[gallery.serialize() for gallery in other_galleries]

        return {
            "event": event.serialize(),
            "galleries_by_year": gby_dict,
            "other_galleries": og_list
        }, 200

@api.route('/get-images/<gallery_slug>')
class GetImagies(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self, gallery_slug):
        '''Get the list of approved images path of a given gallery'''
        page = request.json.get("page")
        page_size = request.json.get("page_size")
        without_base64 = request.json.get("without_base64")

        if without_base64 == None:
            without_base64 = False

        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Not found",
                "body": "Aucune gallerie ne correspond à : "+gallery_slug
            }, 404

        current_user = UserDAO.get_by_id(get_jwt_identity())
        if gallery.private and not GalleryDAO.has_right_on(gallery, current_user):
            return {
                "title": "Erreur - Forbidden",
                "body": "Vous n'avez pas les droits pour accéder à : "+gallery_slug
            }, 403

        list_of_files = FileDAO.find_files_by_gallery(gallery, page, page_size)
        list_of_dim = []
        encoded_list_of_files = []

        for file in list_of_files:
            with open(THUMBS_FOLDER + file.get_thumb_path(), "rb") as image_file:
                encoded = "data:image/"+file.extension+";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
                encoded_list_of_files.append(encoded)
            image_file.close()

            im = Image.open("/app/ponthe/data/galleries/" + file.file_path)
            width, height = im.size
            list_of_dim.append({"width": width, "height": height})


        approved_files = []
        if(without_base64):
            for i in range(len(list_of_files)):
                approved_files.append({
                    'file_path': list_of_files[i].file_path,
                    'full_dimension': list_of_dim[i],
                })
        else:
            for i in range(len(list_of_files)):
                approved_files.append({
                    'file_path': list_of_files[i].file_path,
                    'full_dimension': list_of_dim[i],
                    'base64': encoded_list_of_files[i]
                })

        return {
            "gallery": gallery.serialize(),
            "approved_files": approved_files
        }, 200

@api.route('/get-full-image')
@api.doc(params=    {
                        'file_path': 'Relative path of the file : galleryslug/filename'
                    })
class GetFullImage(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        '''Get a given image in full size base 64'''

        file_path = request.json.get('file_path')

        im = Image.open("/app/ponthe/data/galleries/" + file_path)
        width, height = im.size

        with open("/app/ponthe/data/galleries/" + file_path, "rb") as image_file:
            file = "data:image/"+im.format+";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
        image_file.close()

        return {
            "width": width,
            "height": height,
            "base64": file
        }, 200

@api.route('/get-full-image-raw')
@api.doc(params=    {
                        'file_path': 'Relative path of the file : galleryslug/filename'
                    })
@api.representation('application/binary')
class GetFullImageRaw(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        '''Get a given image in full size raw'''

        file_path = request.json.get('file_path')
        im = Image.open("/app/ponthe/data/galleries/" + file_path)

        return send_file(
            open("/app/ponthe/data/galleries/" + file_path, 'rb'),
            mimetype='image/'+im.format
            )

@api.route('/get-thumb-image-raw/<file_slug>')
@api.doc(params=    {
                        'file_path': 'Relative path of the file : galleryslug/filename'
                    })
@api.representation('application/binary')
class GetFullImageRawGet(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self, file_slug):
        '''Get a given image in small size raw'''

        # <file_slug> dans l'url sert uniquement à empecher le front de mettre en cache
        # les images alors qu'elles sont différentes entre 2 appels

        file_path = request.json.get('file_path')

        print("file_path")
        print(file_path)
        path, filename = os.path.split(file_path)
        slug, extension = os.path.splitext(filename)
        print(slug)
        file = FileDAO().find_by_slug(slug)

        im = Image.open("/app/ponthe/data/galleries/" + file_path)

        return send_file(
            open(THUMBS_FOLDER + file.get_thumb_path(), "rb"),
            mimetype='image/'+im.format
            )

@api.route('/get-random-image/<gallery_slug>')
class GetRandomImage(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def get(self, gallery_slug):
        '''Get the a random image of the given gallery'''
        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Not found",
                "body": "Aucune gallerie ne correspond à : "+gallery_slug
            }, 404

        current_user = UserDAO.get_by_id(get_jwt_identity())
        if gallery.private and not GalleryDAO.has_right_on(gallery, current_user):
            return {
                "title": "Erreur - Forbidden",
                "body": "Vous n'avez pas les droits pour accéder à : "+gallery_slug
            }, 403
        list_of_files = list(filter(lambda file: not file.pending, gallery.files))
        i = random.randint(0, len(list_of_files)-1)
        with open(THUMBS_FOLDER + list_of_files[i].get_thumb_path(), "rb") as image_file:
            encoded_string = str(base64.b64encode(image_file.read()).decode('utf-8'))
        image_file.close()
        return {
            "gallery": gallery.serialize(),
            "thumbnail": encoded_string,
            "url": list_of_files[i].file_path
        }, 200


@api.route('/get-latest-images')
@api.doc(params=    {
                        'page_size': 'number of images',
                        'page': 'page 1 refers to the latest, page 2 refers to the next one...'
                    })
class GetLatestImages(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        page = request.json.get("page")
        page_size = request.json.get("page_size")
        without_base64 = request.json.get("without_base64")

        if(without_base64 == None):
            without_base64 = False


        files = FileDAO().find_all_sorted_by_date(page, page_size)
        list_of_files = list(filter(lambda file: not file.pending, files))
        encoded_list_of_files = []
        list_of_dim = []

        for file in list_of_files:
            with open(THUMBS_FOLDER + file.get_thumb_path(), "rb") as image_file:
                encoded = "data:image/"+file.extension+";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
                encoded_list_of_files.append(encoded)
            image_file.close()

            im = Image.open("/app/ponthe/data/galleries/" + file.file_path)
            width, height = im.size
            list_of_dim.append({"width": width, "height": height})


        latest_files = []
        for i in range(len(list_of_files)):
            if list_of_files[i].pending == False:
                if without_base64:
                    latest_files.append({
                        "file_path": list_of_files[i].file_path,
                        "full_dimension": list_of_dim[i]
                    })
                else:
                    latest_files.append({
                        "file_path": list_of_files[i].file_path,
                        "base64": encoded_list_of_files[i],
                        "full_dimension": list_of_dim[i]
                    })

        return {
            "latest_files": latest_files
        }, 200

@api.route('/galleries/<gallery_slug>')
class Gallery(Resource):
    @jwt_required
    def delete(self, gallery_slug):
        current_user = UserDAO.get_by_id(get_jwt_identity())
        if current_user.admin:
            try:
                GalleryService.delete(gallery_slug, current_user)
                return {}, 200
            except:
                return {'msg': 'Galleries does not exist'}, 404
        return {}, 403

@api.route('/get-latest-galleries')
@api.doc(params=    {
                        'page_size': 'number of images',
                        'page': 'page 1 refers to the latest, page 2 refers to the next ones...'
                    })
class GetLatestGalleries(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        page = request.json.get("page")
        page_size = request.json.get("page_size")

        public_galleries = GalleryDAO().find_all_sorted_by_date(page, page_size)
        gallery_list =[]

        for gallery in public_galleries:
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


@api.route('/galleries/makepublic')
@api.doc(params=    {
                        'gallery_slugs': 'List of slugs of the galleries to be set public'
                    })
class MakeGalleryPublic(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Turn the given galleries public'''
        current_user = UserDAO.get_by_id(get_jwt_identity())
        if not current_user.admin:
            return {"msg": "Unauthorized: you're not an admin"}, 403
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

@api.route('/galleries/makeprivate')
@api.doc(params=    {
                        'gallery_slugs': 'List of slugs of the galleries to be set private'
                    })
class MakeGalleryPublic(Resource):
    @jwt_required
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    def post(self):
        '''Turn the given galeries private'''
        current_user = UserDAO.get_by_id(get_jwt_identity())
        if not current_user.admin:
            return {"msg": "Unauthorized: you're not an admin"}, 403
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

# @api.route('/dashboard')
# class Dashboard(Resource):
#     @jwt_required
#     @api.response(200, 'Success')
#     @api.response(401, 'Error while fetching datas')
#     def post(self):
#         current_user = UserDAO.get_by_id(get_jwt_identity())
#         try:
#             pending_files_by_gallery, confirmed_files_by_gallery = GalleryService.get_own_pending_and_approved_files_by_gallery(current_user)
#         except Exception as e:
#             return {
#                 "title": "Erreur - Impossible de récupérer les données.",
#                 "body": "Une erreur est survenue : "+str(e)
#             }, 401
#
#         return {
#             "pending_files_by_gallery": pending_files_by_gallery,
#             "confirmed_files_by_gallery": confirmed_files_by_gallery
#         }, 200
