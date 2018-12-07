from ..models import User


class UserDAO:
    def __init__(self):
        super().__init__(User)

    @staticmethod
    def find_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_username(username: str):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(id: int):
        return User.query.get(id)