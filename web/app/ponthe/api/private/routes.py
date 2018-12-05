from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO, EventDAO
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
from ...services import UserService
from flask import request


@api.route('/materiel')
class Materiel(Resource):
    @jwt_required
    def post(self):
        object = request.json.get('object')
        message = request.json.get('message')
        if not message:
            return  {
                "title": "Erreur - Aucun message",
                "body": "Veuillez saisir un message"
            }, 406
        current_user = UserDAO.get_by_id(get_jwt_identity())
        msg = Message(subject=f"Demande d'emprunt de {object} par {current_user.firstname} {current_user.lastname}",
                      body=message,
                      sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                      recipients=['alexperez3498@hotmail.fr'])#['ponthe@liste.enpc.fr'])
        mail.send(msg)
        return  {
            "msg": "Mail envoyé !"
        }, 200

@api.route('/years/<year_slug>')
class Year(Resource):
    @jwt_required
    def post(self, year_slug):
        # year_dao = YearDAO()
        # current_user = UserDao().get_by_id(get_jwt_identity)
        # try:
        #     year = year_dao.find_by_slug(year_slug)
        # except NoResultFound:
        #     return {'msg': 'year not found'}, 404
        #
        # public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))

        employeeList = []

        # create a instances for filling up employee list
        for i in range(0,2):
            empDict = {
                'firstName': 'Roy',
                'lastName': 'Augustine'
            }
            employeeList.append(empDict)
        # convert to json data


        return jsonify(Employees=employeeList)
        # ('year_gallery.html', year=year, public_galleries=public_galleries)

@api.route('/years')
class Year(Resource):
    def post(self):
        # year_dao = YearDAO()
        # current_user = UserDao().get_by_id(get_jwt_identity)
        # try:
        #     year = year_dao.find_by_slug(year_slug)
        # except NoResultFound:
        #     return {'msg': 'year not found'}, 404
        #
        # public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))

        table = request.json.get('Employees')
        print(table)
        print(table[0])
        print(table[1])
        # ('year_gallery.html', year=year, public_galleries=public_galleries)

    @jwt_required
    def delete(self, year_slug):
        if current_user.admin:
            try:
                year_dao.delete_detaching_galleries(year_slug)
                return 200
            except:
                return 200

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
                "body": "Une erreur est survenue lors de la création de la gallerie. Probablement qu'un des objets donné n'existe pas (year ou event)."
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

@api.route('/delete-event/<event_slug>')
class DeleteEvent(Resource):
    @jwt_required
    def post(self, event_slug):
        event_dao = EventDAO()

        current_user = UserDAO.get_by_id(get_jwt_identity())

        if current_user.admin:
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

        return {
            "title": "Erreur - Impossible de supprimer l'événement",
            "body": "L'utilisateur n'est pas administrateur"
        }, 401

@api.route('/get-event/<event_slug>')
class Events(Resource):
    @jwt_required
    def post(self, event_slug):
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


        return {
            "event": jsonify(event),
            "galleries_by_year": jsonify(event),
            "other_galleries": jsonify(other_galleries)
        }, 200
