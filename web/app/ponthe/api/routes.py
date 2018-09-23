from . import api
import os, datetime
from ..models import User
from flask import jsonify, request
from .. import db, app
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

jwt = JWTManager(app)

with open(os.path.join(app.instance_path, "keys", "jwtRS256-public.pem"), 'r') as public_key:
    app.config['JWT_PUBLIC_KEY'] = public_key.read()
with open(os.path.join(app.instance_path, "keys", "jwtRS256-private.pem"), 'r') as private_key:
    app.config['JWT_PRIVATE_KEY'] = private_key.read()

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
        print("User authenticating on API :", user)
        access_token = create_access_token(identity=user)
        return jsonify(token=access_token), 200
    else:
        return jsonify({"msg": "Bad email or password"}), 401

@api.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200