from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO
from itsdangerous import SignatureExpired, BadSignature
from ...config import constants
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
