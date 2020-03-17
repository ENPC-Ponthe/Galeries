from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask import request

from . import api
from ... import db


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
