from ..models import Reaction, User, Resource


class ReactionDAO:
    @staticmethod
    def find_by_slug_and_user(slug: str, user: User):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug, Reaction.user == user).first()

    @staticmethod
    def find_all_by_slug(slug: str):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug).all()
    
    @staticmethod
    def find_all_by_user(user: User):
        return Reaction.query.filter_by(user=user).all()
