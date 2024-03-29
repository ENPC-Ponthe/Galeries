from flask import render_template
from flask_login import login_user
from flask_jwt_extended import create_access_token

from ..dao import UserDAO
from ..models import User
from ..config import Constants
from .. import app, db, cas, cas_v2


class CasLoginService:
    # V1 login, not used anymore ?
    @classmethod
    def login(cls):
        app.logger.info('Logging user via CAS: ', cas.username)
        app.logger.debug('with attributes: ', cas.attributes)
        return cls.authenticate(cas.attributes['cas:mail'],
                                cas.attributes['cas:cn'],
                                cas.attributes['cas:givenName'],
                                cas.attributes['cas:sn'])

    # V1 auth, not used anymore ?
    @classmethod
    def authenticate(cls, email, fullname, firstname, lastname):
        if '@eleves.enpc.fr' not in email:
            app.logger.error(f'CAS login failed because email {email} is not a student\'s one')
            return render_template('mail_confirmation.html',
                           title='Erreur - Utilisateur non-autorisé',
                           body='Ce compte DSI n\'appartient pas à un élève, les membres de l\'administration et les prof'
                                'esseurs ne sont pas autorisés.'
                           )
        user = UserDAO.find_by_email(email)
        if user is None:
            user = cls.create_user(email, fullname, firstname, lastname)
        login_user(user)


    @staticmethod
    def create_user(email, fullname, firstname, lastname):
        app.logger.warn(f'Creation of user {fullname} through CAS login')
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
        app.logger.info('Logging user via CAS: ', cas.username)
        app.logger.debug('with attributes: ', cas.attributes)
        return cls.authenticate_v2(cas.attributes['cas:mail'],
                            cas.attributes['cas:cn'],
                            cas.attributes['cas:givenName'],
                            cas.attributes['cas:sn'])

    @classmethod
    def authenticate_v2(cls, email, fullname, firstname, lastname):
        if '@eleves.enpc.fr' not in email:
            app.logger.error(f'CAS login failed because email {email} is not a student\'s one')
            return { 'title': 'Erreur - Utilisateur non-autorisé',
                    'body': 'Ce compte DSI n\'appartient pas à un élève, les membres de l\'administration et les prof'
                                'esseurs ne sont pas autorisés.'
            }
        user = UserDAO.find_by_email(email)
        if user is None:
            user = cls.create_user(email, fullname, firstname, lastname)
        login_user(user)
        access_token = create_access_token(identity=user)
        return access_token
