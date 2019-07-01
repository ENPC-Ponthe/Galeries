from . import api
from flask_restplus import Resource
import re
import os, datetime
from ...models import User
from ...services import UserService
from ...dao import UserDAO
from flask import request
import json
from ... import db, app
from flask_jwt_extended import JWTManager, create_access_token
from itsdangerous import SignatureExpired, BadSignature


jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {
        "username" : user.username,
        "firstname" : user.firstname,
        "lastname" : user.lastname,
        "roles" : ["USER", "ADMIN"] if user.admin else ["USER"]
    }

@jwt.user_identity_loader
def user_identity(user):
    return user.id

# Returned user accessed using the get_current_user() function, or directly with the current_user LocalProxy
@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return UserDAO.get_by_id(identity)


@api.route('/login')
@api.doc(params=    {
                        'email': 'the whole email. Example : jean.dupont@eleves.enpc.fr',
                        'password': 'your password'
                    })
class Login(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    @api.response(401, 'User not identified - incorrect email or password')
    def post(self):
        if not request.is_json:
            return {"msg": "Missing JSON in request"}, 400

        email = request.json.get('email', None)
        password = request.json.get('password', None)
        if not email:
            return {"msg": "Missing email parameter"}, 400
        if not password:
            return {"msg": "Missing password parameter"}, 400

        user = User.query.filter_by(email=email).first()

        if user is None:
            return {"msg": "Identifiants incorrectes"}, 401
        if not user.email_confirmed:
            if (datetime.datetime.utcnow()-user.created).total_seconds() > 3600:
                db.session.delete(user)
                db.session.commit()
            else:
                return {"msg": "Compte en attente de confirmation par email"}, 403
        if user.check_password(password):
            app.logger.debug("User authenticating on API :", user)
            access_token = create_access_token(identity=user)
            return {"token": access_token}, 200
        else:
            return {"msg": "Bad email or password"}, 401


@api.route('/register')
@api.response(200, 'Success')
@api.response(400, 'Request incorrect - JSON not valid. Email not allowed or password and confirmation_password not equals')
@api.response(403, 'Unauthorized - account already exists')
@api.doc(params=    {
                        'lastname': '-',
                        'firstname': '-',
                        'email': '1st part of the email. Example : jean.dupont',
                        'password': 'your password',
                        'confirmation_password': 'confirmation of your password',
                        'promotion': 'the year you graduate. Example : 020'
                    })
class Register(Resource):
    def post(self):
        lastname = request.json.get('lastname')
        firstname = request.json.get('firstname')
        username = request.json.get('email')
        password = request.json.get('password')
        promotion = request.json.get('promotion')
        if password != request.json.get('confirmation_password'):
            return {"msg": "Les deux mot de passe ne correspondent pas"}, 400
        elif not re.fullmatch(r"[a-z0-9\-]+\.[a-z0-9\-]+", username):
            return {"msg": "Adresse non valide"}, 400
        else:
            try:
                UserService.register(username, firstname, lastname, password, promotion)
            except ValueError:
                return {"msg": "Il existe déjà un compte pour cet adresse email"}, 403
        return {"msg": "utilisateur créé"}, 200


@api.route('/reset/')
@api.response(200, 'Success - Password Resel Email sent.')
@api.doc(params=    {
                        'email': 'the whole email. Example : jean.dupont@eleves.enpc.fr',
                    })
class ResetPasswordSendMail(Resource):
    def post(self):
        email = request.json.get('email')
        UserService.reset(email)
        return {"msg": "Si un compte est associé à cette adresse, un mail a été envoyé"}, 200

@api.route('/reset/<token>')
@api.response(200, 'Success - Password updated')
@api.response(404, 'Not Found - invalid token')
@api.response(403, 'Unauthorized - token expired')
@api.response(401, 'User not identified - account not found')
@api.response(400, 'Bad Request - new_password and confirmation_password not equals')
@api.doc(params=    {
                        'new_password': '-',
                        'confirmation_password': 'confirmation of your new password'
                    })
class PasswordResetForm(Resource):
    def post(self, token):
        try:
            user_id = UserService.get_id_from_token(token)
            if user_id is None:
                return {"msg": "compte introuvable"}, 404
        except BadSignature:
            return {"msg": "token invalide"}, 404
        except SignatureExpired :
            return  {
                        "title": "Le token est expiré",
                        "body": "Tu as dépassé le délai de 24h."
                    }, 403
        user = UserDAO.get_by_id(user_id)
        if user is None:
            return  {
                        "title": "Erreur - Aucun utilisateur correspondant",
                        "body": "Le compte associé n'existe plus"
                    }, 401

        new_password = request.json.get('new_password')
        if new_password != request.json.get('confirmation_password'):
            return {"msg": "Les deux mots de passe ne correspondent pas"}, 400
        else:
            user.set_password(new_password)
            db.session.add(user)
            db.session.commit()
            return {"msg": "Mot de passe réinitialisé avec succès"}, 200


@api.route('/cgu')
@api.response(200, 'Success')
class Cgu(Resource):
    def get(self):
        """
            Return the General Conditions of Use
        """
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        cgu = open(os.path.join(SITE_ROOT, "/app/ponthe/templates", "cgu.json"))
        return json.load(cgu, strict=False), 200
