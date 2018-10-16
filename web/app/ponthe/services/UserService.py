from flask import url_for
from itsdangerous import URLSafeTimedSerializer
from ponthe.models import User

from .. import app

serializer=URLSafeTimedSerializer(app.secret_key)

class UserService:
    @staticmethod
    def get_token(user: User):
        return serializer.dumps(user.id)

    @staticmethod
    def get_id_from_token(token: str):
        return serializer.loads(token, max_age=3600)

    def get_reset_link(self, user: User):
        return "https://ponthe.enpc.org"+url_for('public.resetting', token=self.get_token(user))
