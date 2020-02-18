from flask import render_template
from flask_login import login_user
from flask_jwt_extended import create_access_token

from ..dao import UserDAO
from ..models import User
from ..config import Constants
from .. import app, db, cas, cas_v2


class CasLoginService:
    @classmethod
    def login(cls):
        app.logger.info("Logging user via CAS: ", cas.username)
        app.logger.debug("with attributes: ", cas.attributes)
        return cls.authenticate(cas.attributes['cas:mail'],
                                cas.attributes['cas:cn'],
                                cas.attributes['cas:givenName'],
                                cas.attributes['cas:sn'])

    @classmethod
    def authenticate(cls, email, fullname, firstname, lastname):
        if '@eleves.enpc.fr' not in email:
            app.logger.error(f"CAS login failed because email {email} is not a student's one")
            return render_template('mail_confirmation.html',
                           title="Erreur - Utilisateur non-autorisé",
                           body="Ce compte DSI n'appartient pas à un élève, les membres de l'administration et les prof"
                                "esseurs ne sont pas autorisés."
                           )
        user = UserDAO.find_by_email(email)
        if user is None:
            user = cls.create_user(email, fullname, firstname, lastname)
        login_user(user)


    @staticmethod
    def create_user(email, fullname, firstname, lastname):
        app.logger.warn(f"Creation of user {fullname} through CAS login")
        new_user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=User.generate_random_password(),
            promotion=Constants.LAST_PROMOTION,
            admin=False,
            email_confirmed=True
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    @classmethod
    def login_v2(cls):
        try:
            app.logger.info("Logging user via CAS: ", cas_v2.username)
            app.logger.debug("with attributes: ", cas_v2.attributes)
        except:
            return "Erreur pour log au début du login"
        try:
            return cls.authenticate_v2(cas_v2.attributes['cas:mail'],
                                cas_v2.attributes['cas:cn'],
                                cas_v2.attributes['cas:givenName'],
                                cas_v2.attributes['cas:sn'])
        except:
            return 'Erreur dans authenticate_v2, le reste fonctionne.' + cas_v2.attributes

    @classmethod
    def authenticate_v2(cls, email, fullname, firstname, lastname):
        try:
            if '@eleves.enpc.fr' not in email:
                app.logger.error(f"CAS login failed because email {email} is not a student's one")
                return { "title": "Erreur - Utilisateur non-autorisé",
                        "body": "Ce compte DSI n'appartient pas à un élève, les membres de l'administration et les prof"
                                    "esseurs ne sont pas autorisés.",
                                    "perso": email + ' ++ ' + fullname + ' ++ ' + firstname + ' ++ ' + lastname
                }
        except:
            return "Erreur car pas bon mail ++ " #+ email + ' ++ ' + fullname + ' ++ ' + firstname + ' ++ ' + lastname
        try:
            user = UserDAO.find_by_email(email)
            if user is None:
                user = cls.create_user(email, fullname, firstname, lastname)
        except:
            return "Erreur pour obtenir le user ++" #+ email + ' ++ ' + fullname + ' ++ ' + firstname + ' ++ ' + lastname
        try:
            login_user(user)
        except:
            return "Erreur pour login le user ++ " #+ email + ' ++ ' + fullname + ' ++ ' + firstname + ' ++ ' + lastname
        try:
            access_token = create_access_token(identity=user)
        except:
            return "Problème de création de token ++" #+ email + " ++ " + fullname + " ++ " + firstname + " ++ " + lastname
        return access_token