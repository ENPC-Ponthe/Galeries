from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_mail import Message
from flask import request

from . import api
from ... import mail

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
        device = request.json.get('device')
        message = request.json.get('message')
        if not message:
            return {
                "title": "Erreur - Aucun message",
                "body": "Veuillez saisir un message"
            }, 400
        msg = Message(subject=f"Demande d'emprunt de {device} par {current_user.firstname} {current_user.lastname}",
                      body=message,
                      sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                      recipients=['ponthe@liste.enpc.fr'])
        mail.send(msg)
        return {
            "msg": "Mail envoyé !"
        }, 200


@api.route('/contact')
@api.doc(params={
    'message': 'your message'
})
class Contact(Resource):
    @api.response(200, 'Success - Mail sent')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Send a mail to ponthe to borrow material'''
        message = request.json.get('message')
        if not message:
            return {
                "title": "Erreur - Aucun message",
                "body": "Veuillez saisir un message"
            }, 400
        msg = Message(subject=f"Message de la part de {current_user.firstname} {current_user.lastname}",
                      body=message,
                      sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                      recipients=['ponthe@liste.enpc.fr'])
        mail.send(msg)
        return {
            "msg": "Mail envoyé !"
        }, 200
