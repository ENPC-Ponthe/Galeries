from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO, EventDAO, GalleryDAO
from itsdangerous import SignatureExpired, BadSignature
from ...config import constants
from sqlalchemy.orm.exc import NoResultFound
import re
import json
from flask import jsonify
# from urllib.parse import urlparse, urljoin
# from flask_login import login_user, current_user
from itsdangerous import SignatureExpired, BadSignature
from datetime import datetime

# from . import public
from ... import app, db, login_manager
from ...services import UserService, GalleryService
from flask import request
# from ...models import serialize



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
                        'object': 'object you would like to borrow to the club',
                        'message': 'your message'
                    })
class Materiel(Resource):
    @jwt_required
    @api.response(200, 'Success - Mail sent')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        object = request.json.get('object')
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
                      recipients=['alexperez3498@hotmail.fr'])#['ponthe@liste.enpc.fr'])
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


@api.route('/years/<year_slug>')
@api.doc(params=    {
                        'year_slug': 'Example : 2018'
                    })
class Year(Resource):
    @jwt_required
    @api.response(200, 'Success')
    def get(self, year_slug):
        year_dao = YearDAO()
        try:
            return year_dao.serialize(year_slug), 200
        except NoResultFound:
            return {'msg': 'year not found'}, 404

    @jwt_required
    @api.response(200, 'Success')
    @api.response(40, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - not admin')
    @api.response(401, 'User not identified - incorrect email or password')
    def delete(self, year_slug):
        year_dao = YearDAO()
        current_user = UserDao().get_by_id(get_jwt_identity)
        if current_user.admin:
            try:
                 year_dao.delete_detaching_galleries(year_slug)
                 return {'msg': 'year deleted'}, 200
            except NoResultFound:
                 return {'msg': 'year not found'}, 404
        return {'msg': 'not admin'}, 403


@api.route('/create-gallery')
class CreateGallery(Resource):
    @jwt_required
    def post(self):
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
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        members = open(os.path.join(SITE_ROOT, "/app/ponthe/templates", "members.json"))
        return json.load(members, strict=False)



@api.route('/get-galleries/<event_slug>')
class GetGalleries(Resource):
    @jwt_required
    def get(self, event_slug):
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

@api.route('/get-imagies/<gallery_slug>')
class GetImagies(Resource):
    @jwt_required
    def get(self, gallery_slug):
        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {
                "title": "Erreur - Not found",
                "body": "Aucune gallerie ne correspond à : "+gallery_slug
            }, 404
        if gallery.private and not GalleryDAO.has_right_on(gallery):
            return {
                "title": "Erreur - Forbidden",
                "body": "Vous n'avez pas les droits pour accéder à : "+gallery_slug
            }, 403
        return {
            "gallery": gallery.serialize(),
            "approved_files": list(filter(lambda file: not file.pending, gallery.files))
        }, 200


@api.route('/galleries/<gallery_slug>')
class Gallery(Resource):
    def post(self, gallery_slug):
        try:
            gallery = GalleryDAO().find_by_slug(gallery_slug)
        except NoResultFound:
            return {"msg": "Error: "}
        if gallery.private and not GalleryDAO.has_right_on(gallery):
            raise NotFound()
        return render_template('gallery.html', gallery=gallery, approved_files=filter(lambda file: not file.pending, gallery.files))
    @jwt_required
    def delete(self, gallery_slug):
        current_user = UserDao().get_by_id(get_jwt_identity)
        if current_user.admin:
            try:
                GalleryService.delete(gallery_slug)
            except:
                return {'msg': 'Galleries does not exist'}, 404


@api.route('/galleries/makepublic')
class MakeGalleryPublic(Resource):
    def post(self):
        current_user = UserDao().get_by_id(get_jwt_identity)
        if not current_user.admin:
            return {"msg": "Unauthorized: you're not an admin"}, 403
        ListOfGallerySlugs = request.json.get('gallery_slugs')
        ListOfGalleryFailedToMakePublic = []
        for gallery_slug in ListOfGallerySlugs:
            try:
                GalleryService.make_public(gallery_slug)
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
class MakeGalleryPublic(Resource):
    def post(self):
        current_user = UserDao().get_by_id(get_jwt_identity)
        if not current_user.admin:
            return {"msg": "Unauthorized: you're not an admin"}, 403
        ListOfGallerySlugs = request.json.get('gallery_slugs')
        ListOfGalleryFailedToMakePublic = []
        for gallery_slug in ListOfGallerySlugs:
            try:
                GalleryService.make_private(gallery_slug)
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

@api.route('/dashboard')
class Dashboard(Resource):
    @jwt_required
    def post(self):
        current_user = UserDAO.get_by_id(get_jwt_identity())
        try:
            pending_files_by_gallery, confirmed_files_by_gallery = GalleryService.get_own_pending_and_approved_files_by_gallery(current_user)
        except Exception as e:
            return {
                "title": "Erreur - Impossible de récupérer les données.",
                "body": "Une erreur est survenue : "+str(e)
            }, 401

        return {
            "pending_files_by_gallery": pending_files_by_gallery,
            "confirmed_files_by_gallery": confirmed_files_by_gallery
        }, 201