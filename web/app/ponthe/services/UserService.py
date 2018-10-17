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
        return f"ponthe.enpc.org/reset/{self.get_token(user)}"
