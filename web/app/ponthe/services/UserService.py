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

    @classmethod
    def get_reset_link(cls, user: User):
        return f"ponthe.enpc.org/reset/{cls.get_token(user)}"
