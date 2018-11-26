from . import api
import re
import os, datetime
from ..models import User
from ..services import UserService
from flask import jsonify, request
from .. import db, app
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

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
    return User.query.filter_by(id=identity).first()

@api.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "Identifiants incorrectes"}), 404
    if not user.email_confirmed:
        if (datetime.utcnow()-user.created).total_seconds() > 3600:
            db.session.delete(user)
            db.session.commit()
        else:
            return jsonify({"msg": "Compte en attente de confirmation par email"}), 400
    if user.check_password(password):
        app.logger.debug("User authenticating on API :", user)
        access_token = create_access_token(identity=user)
        return jsonify(token=access_token), 200
    else:
        return jsonify({"msg": "Bad email or password"}), 401

@api.route('/register', methods=['POST'])
def register():
    lastname = request.json.get('lastname')
    firstname = request.json.get('firstname')
    username = request.json.get('email')
    password = request.json.get('password')
    promotion = request.json.get('promotion')
    if password != request.json.get('confirmation_password'):
        return jsonify({"msg": "les deux mot de passe ne correspondent pas"}), 401
    elif not re.fullmatch(r"[a-z0-9\-]+\.[a-z0-9\-]+", username):
        return jsonify({"msg": "adresse non valide"}), 401
    else:
        try:
            new_user = UserService.register(username, firstname, lastname, password, promotion)
        except ValueError:
            return jsonify({"msg": "Il existe déjà un compte pour cet adresse email"}), 401
    return jsonify({"msg": "utilisateur créé"}), 200

@api.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@api.route('/reset', methods=['POST'])
def reset():
    email = request.json.get['email']
    UserService.reset(email)
    return json({"msg": "si un compte est associé à cette adresse, un mail a été envoyé"}), 200

@api.route('/reset/<token>', methods=['GET', 'POST'])
def resetting(token):
    try :
        user_id = UserService.get_id_from_token(token)
        if user_id is None:
            abort(404)
    except BadSignature:
        abort(404)
    except SignatureExpired :
        return jsonify(
            {
                "title": "Le token est expiré",
                "body": "Tu as dépassé le délai de 24h."
            }
        ), 401

    user = UserDAO.get_by_id(user_id)
    if user is None:
        return jsonify(
            {
                "title": "Erreur - Aucun utilisateur correspondant",
                "body": "Le compte associé n'existe plus"
            }
        ), 401

    if request.method == 'POST':
        new_password = request.json.get('new_password')
        if new_password != request.json.get('confirmation_password'):
            return jsonify({"msg": "Les deux mots de passe ne correspondent pas"}), 401
        else:
            user.set_password(new_password)
            db.session.add(user)
            db.session.commit()
            return jsonify({"msg": "Mot de passe réinitialisé avec succès"}), 200

    return render_template('resetting.html', firstname=user.firstname)

@api.route('/cgu')
def cgu():
    return render_template('cgu.html')
