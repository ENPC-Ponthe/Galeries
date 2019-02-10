from datetime import datetime

from itsdangerous import URLSafeTimedSerializer
from .MailService import MailService

from ..persistence import UserDAO
from sqlalchemy.exc import IntegrityError

from ..models import User

from .. import app, db

serializer=URLSafeTimedSerializer(app.secret_key)

class UserService:
    @staticmethod
    def get_token(user: User):
        return serializer.dumps(user.id)

    @staticmethod
    def get_id_from_token(token: str):
        return serializer.loads(token, max_age=3600)

    @classmethod
    def get_reset_link(cls, user: User):
        return f"ponthe-testing.enpc.org/reset/{cls.get_token(user)}"

    @classmethod
    def register(cls, username: str, firstname: str, lastname: str, password: str, promotion: str):
        new_user = User(
            lastname=lastname,
            firstname=firstname,
            username=username,
            password=password,
            promotion=promotion,
            admin=False,
            email_confirmed=False
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            existing_user = UserDAO.find_by_username(new_user.username)

            if not existing_user.email_confirmed and (datetime.utcnow() - existing_user.created).total_seconds() > 3600:
                db.session.delete(existing_user)
                db.session.commit()
                db.session.add(new_user)
                db.session.commit()
            else:
                raise ValueError

        token = cls.get_token(new_user)
        MailService.send_registering_email(new_user.firstname, new_user.email, token)

        return new_user

    @classmethod
    def reset(cls, email:str):
        user = UserDAO.find_by_email(email)
        if user is not None and user.email_confirmed:
            reset_link = cls.get_reset_link(user)
            MailService.send_resetting_email(user.firstname, user.email, reset_link)
