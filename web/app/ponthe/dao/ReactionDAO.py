from ..models import Reaction, User, Resource


class ReactionDAO:
    def __init__(self):
        super().__init__(Reaction)

    @staticmethod
    def find_by_slug_and_user(slug: str, user: User):
        return Reaction.query.join(Resource.slug).filter(Resource.slug == slug, Reaction.user == user).one()

    @staticmethod
    def find_all_by_slug(slug: str):
        return Reaction.query.join(Resource.slug).filter_by(Resource.slug == slug).all()
    
    @staticmethod
    def find_all_by_user(user: User):
        return Reaction.query.filter_by(Reaction.user == user).all()
