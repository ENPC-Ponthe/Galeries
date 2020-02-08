import random
import base64
import os
import time
import json

from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_mail import Message
from sqlalchemy.orm.exc import NoResultFound
from flask import send_file
from werkzeug.utils import secure_filename
from flask import request
from PIL import Image

from . import api
from ... import db, mail, app
from ...dao import YearDAO, EventDAO, GalleryDAO, FileDAO
from ...services import GalleryService
from ...file_helper import is_allowed_file, get_base64_encoding
from ...services import FileService


UPLOAD_FOLDER = app.config['MEDIA_ROOT']
ASSET_FOLDER = app.config['ASSET_ROOT']


@api.route('/file-upload/<gallery_slug>')
@api.doc(params={
    'file': 'file to upload',
})
class Upload(Resource):
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

        if file and is_allowed_file(file.filename):
            filename = secure_filename(base64.b64encode(bytes(str(time.time()) + file.filename,'utf-8')).decode('utf-8')+ "." + file.filename.rsplit('.', 1)[1].lower())
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            FileService.create(os.path.join(UPLOAD_FOLDER, filename), filename, gallery_slug, current_user)
            return {
                "msg": "File has been saved"
            }, 200


@api.route('/get-user-by-jwt')
class GetUser(Resource):
    @api.response(200, 'Success')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        return {
            "firstname": current_user.firstname,
            "lastname": current_user.lastname,
            "email": current_user.email,
            "admin": current_user.admin,
            "promotion": current_user.promotion
        }, 200


@api.route('/materiel')
@api.doc(params={
    'device': 'object you would like to borrow to the club',
    'message': 'your message'
})
class Materiel(Resource):
    @api.response(200, 'Success - Mail sent')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Send a mail to ponthe to borrow material'''
        object = request.json.get('device')
        message = request.json.get('message')
        if not message:
            return {
                "title": "Erreur - Aucun message",
                "body": "Veuillez saisir un message"
            }, 400
        msg = Message(subject=f"Demande d'emprunt de {object} par {current_user.firstname} {current_user.lastname}",
                      body=message,
                      sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                      recipients=['alexperez3498@hotmail.fr', 'ponthe@liste.enpc.fr'])#['ponthe@liste.enpc.fr'])
        mail.send(msg)
        return {
            "msg": "Mail envoyé !"
        }, 200


@api.route('/get-galleries-of-year/<year_slug>')
@api.doc(params={
    'year_slug': 'Example : 2018'
})
class Year(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Year not found')
    def get(self, year_slug):
        '''Get the list of public galleries of a given year'''
        year_dao = YearDAO()
        try:
            year = year_dao.find_by_slug(year_slug)
            public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
            return {
                "year": year_dao.serialize(year_slug),
                "public_galleries": [gallery.slug for gallery in public_galleries]
            }, 200
        except NoResultFound:
            return {'msg': 'year not found'}, 404

    @api.response(200, 'Success')
    @api.response(40, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - not admin')
    def delete(self, year_slug):
        '''Delete a given year'''
        year_dao = YearDAO()
        if current_user.admin:
            try:
                 year_dao.delete_detaching_galleries(year_slug)
                 return {'msg': 'year deleted'}, 200
            except NoResultFound:
                 return {'msg': 'year not found'}, 404
        return {'msg': 'not admin'}, 403


@api.route('/get-galleries-by-year')
class GetGalleriesByYear(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Year not found')
    def post(self):
        '''Get the list of public galleries of all years'''

        without_base64 = request.json.get('without_base64')

        if without_base64 is None:
            without_base64 = False

        year_dao = YearDAO()
        year_list = year_dao.find_all_ordered_by_value()
        data = []
        for year in year_list:
            public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
            gallery_list = []
            for gallery in public_galleries:
                list_of_files = list(filter(lambda file: not file.pending, gallery.files))
                if list_of_files:
                    i = random.randint(0, len(list_of_files)-1)
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
                            "image": FileService.get_base64_encoding_thumb(list_of_files[i])
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
    @api.response(200, 'Success')
    def get(self):
        '''Get the list of public galleries of all years'''
        gallery_list = []
        public_galleries = GalleryDAO().find_all_public_sorted_by_date()
        for gallery in public_galleries:
            list_of_files = list(filter(lambda file: not file.pending, gallery.files))
            if list_of_files:
                i = random.randint(0, len(list_of_files)-1)
                encoded_string = FileService.get_base64_encoding_large_thumb(list_of_files[i])
            else:
                encoded_string = ""
            gallery_list.append({
                "name": gallery.name,
                "slug": gallery.slug,
                "image": encoded_string
            })
        data =  {
                    "galleries": gallery_list
                }
        return data, 200

# TEST
@api.route('/get-all-galleries-restricted')
class GetAllGalleriesRestricted(Resource):
    @api.response(200, 'Success')
    def get(self):
        user_promotion = current_user.promotion
        full_promotion_year = int('2' + user_promotion)
        starting_year = full_promotion_year - 3
        ending_year = starting_year + 2
        data= { "starting_year": starting_year, "ending_year": ending_year}
        # '''Get the list of public galleries of all years'''
        # gallery_list = []
        # public_galleries = GalleryDAO().find_all_public_sorted_by_date_filtered_by_years(starting_year, ending_year)
        # for gallery in public_galleries:
        #     list_of_files = list(filter(lambda file: not file.pending, gallery.files))
        #     if list_of_files:
        #         i = random.randint(0, len(list_of_files)-1)
        #         encoded_string = FileService.get_base64_encoding_large_thumb(list_of_files[i])
        #     else:
        #         encoded_string = ""
        #     gallery_list.append({
        #         "name": gallery.name,
        #         "slug": gallery.slug,
        #         "image": encoded_string
        #     })
        # data =  {
        #             "galleries": gallery_list
        #         }
        return data, 200


@api.route('/create-gallery')
@api.doc(params={
    'name': 'Gallery name',
    'description': '',
    'year_slug': 'Slug of the year of the galery. Ex: 2019',
    'event_slug': 'Slug of the parent event of the galery.',
    'private': 'Boolean'
})
class CreateGallery(Resource):
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
            return {
                "title": "Erreur - Paramètre manquant",
                "body": "Veuillez renseigner le nom de la nouvelle galerie"
            }, 401

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
    def get(self):
        '''Get Ponthe members'''
        with open(os.path.join(ASSET_FOLDER, "data/members.json")) as members:
            return json.load(members, strict=False)


@api.route('/get-galleries/<event_slug>')
class GetGalleries(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'No corresponding event to event_slug')
    def get(self, event_slug: str):
        '''Get the list of galleries of an event'''
        event_dao = EventDAO()

        try:
            event = event_dao.find_by_slug(event_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Impossible de trouver l'événement",
                "body": "Aucun événement ne correspond à : " + event_slug
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
class GetImages(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self, gallery_slug: str):
        '''Get the list of approved images path of a given gallery'''
        page = request.json.get("page")
        page_size = request.json.get("page_size")
        without_base64 = request.json.get("without_base64")

        if without_base64 is None:
            without_base64 = False

        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Not found",
                "body": "Aucune gallerie ne correspond à : " + gallery_slug
            }, 404

        if gallery.private and not GalleryDAO.has_right_on(gallery, current_user):
            return {
                "title": "Error - Forbidden",
                "body": "Vous n'avez pas les droits pour accéder à : " + gallery_slug
            }, 403

        if GalleryDAO.has_right_on(gallery, current_user):
            list_of_files = FileDAO.find_all_files_by_gallery(gallery, page, page_size)
        else:
            list_of_files = FileDAO.find_not_pending_files_by_gallery(gallery, page, page_size)

        list_of_dim = []
        encoded_list_of_files = []

        for file in list_of_files:
            encoded_file = FileService.get_base64_encoding_thumb(file)
            encoded_list_of_files.append(encoded_file)

            im = Image.open(FileService.get_absolute_file_path(file))
            width, height = im.size
            list_of_dim.append({"width": width, "height": height})

        approved_files = []
        if without_base64:
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
            "files": approved_files
        }, 200


@api.route('/get-full-image')
@api.doc(params={
    'file_path': 'Relative path of the file : gallery-slug/filename'
})
class GetFullImage(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        '''Get a given image in full size base 64'''

        file_path = request.json.get('file_path')

        im = Image.open(os.path.join(UPLOAD_FOLDER, file_path))
        width, height = im.size
        im.close()

        return {
            "width": width,
            "height": height,
            "base64": get_base64_encoding(os.path.join(UPLOAD_FOLDER, file_path))
        }, 200


@api.route('/get-full-image-raw')
@api.doc(params={
    'file_path': 'Relative path of the file : galleryslug/filename'
})
@api.representation('application/binary')
class GetFullImageRaw(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        '''Get a given image in full size raw'''

        file_path = request.json.get('file_path')
        absolute_file_path = os.path.join(UPLOAD_FOLDER, file_path)
        im = Image.open(absolute_file_path)

        return send_file(
            open(absolute_file_path, 'rb'),
            mimetype='image/'+im.format
            )


@api.route('/get-thumb-image-raw/<file_slug>')
@api.doc(params={
    'file_path': 'Relative path of the file : galleryslug/filename'
})
@api.representation('application/binary')
class GetFullImageRawGet(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self, file_slug: str):
        '''Get a given image in small size raw'''

        # <file_slug> dans l'url sert uniquement à empecher le front de mettre en cache
        # les images alors qu'elles sont différentes entre 2 appels

        file_path = request.json.get('file_path')

        path, filename = os.path.split(file_path)
        slug, extension = os.path.splitext(filename)
        file = FileDAO().find_by_slug(slug)

        im = Image.open(os.path.join(UPLOAD_FOLDER, file_path))

        return send_file(
            open(FileDAO.get_thumb_path_or_create_it(file), "rb"),
            mimetype='image/'+im.format
            )


@api.route('/get-random-image/<gallery_slug>')
class GetRandomImage(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def get(self, gallery_slug: str):
        '''Get the a random image of the given gallery'''
        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Not found",
                "body": "Aucune gallerie ne correspond à : "+gallery_slug
            }, 404

        if gallery.private and not GalleryDAO.has_right_on(gallery, current_user):
            return {
                "title": "Erreur - Forbidden",
                "body": "Vous n'avez pas les droits pour accéder à : "+gallery_slug
            }, 403

        list_of_files = list(filter(lambda file: not file.pending, gallery.files))
        i = random.randint(0, len(list_of_files)-1)

        return {
            "gallery": gallery.serialize(),
            "thumbnail": FileService.get_base64_encoding_thumb(list_of_files[i]),
            "url": list_of_files[i].file_path
        }, 200


@api.route('/get-latest-images')
@api.doc(params={
    'page_size': 'number of images',
    'page': 'page 1 refers to the latest, page 2 refers to the next one...'
})
class GetLatestImages(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        page = request.json.get("page")
        page_size = request.json.get("page_size")
        without_base64 = request.json.get("without_base64")

        if without_base64 is None:
            without_base64 = False

        files = FileDAO().find_all_moderated_sorted_by_date(page, page_size)
        list_of_files = list(filter(lambda file: not file.pending, files))
        encoded_list_of_files = []
        list_of_dim = []

        for file in list_of_files:
            encoded_file = FileService.get_base64_encoding_thumb(file)
            encoded_list_of_files.append(encoded_file)

            im = Image.open(os.path.join(UPLOAD_FOLDER, file.file_path))
            width, height = im.size
            list_of_dim.append({"width": width, "height": height})


        latest_files = []
        for i in range(len(list_of_files)):
            if not list_of_files[i].pending:
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
            "files": latest_files
        }, 200


@api.route('/get-latest-galleries')
@api.doc(params={
    'page_size': 'number of images',
    'page': 'page 1 refers to the latest, page 2 refers to the next ones...'
})
class GetLatestGalleries(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(404, 'Not found - No matching gallery_slug')
    def post(self):
        page = request.json.get("page")
        page_size = request.json.get("page_size")

        public_galleries = GalleryDAO().find_public_sorted_by_date(page, page_size)
        gallery_list =[]

        for gallery in public_galleries:
            list_of_files = list(filter(lambda file: not file.pending, gallery.files))
            if list_of_files:
                i = random.randint(0, len(list_of_files)-1)
                encoded_string = FileService.get_base64_encoding_full(list_of_files[i])
            else:
                encoded_string = ""
            gallery_list.append({
                "name": gallery.name,
                "slug": gallery.slug,
                "image": encoded_string,
                "description": gallery.description
            })
        data =  {
                    "galleries": gallery_list
                }
        return data, 200


@api.route('/reset-password')
@api.doc(params={
    'current_password': 'your current password',
    'new_password': 'your new password'
})
class ResetPasword(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Unauthorized - JWT not valid')
    def post(self):
        current_password = request.json.get('current_password')
        new_password = request.json.get('new_password')
        if current_user.check_password(current_password):
            current_user.set_password(new_password)
            db.session.add(current_user)
            db.session.commit()
            return {"msg": "Mot de passe réinitialisé avec succès"}, 200
        else:
            return {"msg": "Mot de passe incorrect"}, 400
