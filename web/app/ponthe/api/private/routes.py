from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .. import api
from flask_restplus import Resource
from ...persistence import UserDAO, YearDAO
from itsdangerous import SignatureExpired, BadSignature
from ...config import constants
import re
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
        year_dao = YearDAO()
        current_user = UserDao().get_by_id(get_jwt_identity)
        if request.method == 'POST' and "delete" in request.form and current_user.admin:
            year_dao.delete_detaching_galleries(year_slug)
            return redirect("/index")
        try:
            year = year_dao.find_by_slug(year_slug)
        except NoResultFound:
            return {'msg': 'year not found'}, 404
        public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
        return render_template('year_gallery.html', year=year, public_galleries=public_galleries)

    def delete(self, year_slug):
        if current_user.admin:
            year_dao.delete_detaching_galleries(year_slug)
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
