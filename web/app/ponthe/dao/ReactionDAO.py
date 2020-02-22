from sqlalchemy import desc

from ..models import Reaction, User, Resource


class ReactionDAO:
    @staticmethod
    def find_by_slug_and_user(slug: str, user: User):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug, Reaction.user == user).first()
    
    @staticmethod
    def find_by_resource_id_and_user(resource_id: int, user: User):
        return Reaction.query.filter(resource_id=resource_id, user=user).first()

    @staticmethod
    def find_all_by_slug(slug: str):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug).all()
    
    @staticmethod
    def find_all_by_user(user: User):
        return Reaction.query.filter_by(user=user).all()
    
    @staticmethod
    def find_by_user(user: User, page=None, page_size=None):
        if page_size is None:
            return ReactionDAO().find_all_by_user(user)
        else:
            if page is None:
                page = 1
            return Reaction.query.filter_by(user=user).order_by(desc(Reaction.updated)).offset(
                (page - 1) * page_size).limit(page_size).all()