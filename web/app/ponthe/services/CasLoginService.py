from flask_login import login_user

from ..dao import UserDAO
from ..models import User
from ..config import Constants
from .. import app, db, cas


class CasLoginService:
    @classmethod
    def login(cls):
        app.logger.info("Logging user via CAS: ", cas.username)
        app.logger.info("with attributes: ", cas.attributes)
        cls.authenticate(cas.attributes['mail'])

    @classmethod
    def authenticate(cls, email):
        if '@eleves.enpc.fr' not in email:
            app.logger.warn(f"CAS login failed because email {email} is not a student's one")
            return
        user = UserDAO.find_by_email(email)
        if user is not None:
            login_user(user)
        else:
            cls.create_user(email)


    @staticmethod
    def create_user(email):
        app.logger.info(f"Creation of user {email} through CAS login")
        new_user = User(
            firstname=cas.attributes['givenName'],
            lastname=cas.attributes['sn'],
            email=email,
            password=User.generate_random_password(),
            promotion=Constants.LAST_PROMOTION,
            admin=False,
            email_confirmed=True
        )
        db.session.add(new_user)
        db.session.commit()
