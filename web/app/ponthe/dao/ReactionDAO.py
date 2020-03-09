from sqlalchemy import desc

from ..models import Reaction, User, Resource, GalleryTypeEnum


def query_with_offset(query, page=None, page_size=None):
    if page_size is None:
        return query
    else:
        if page is None:
            page = 1
        return query.offset((page - 1) * page_size).limit(page_size)


class ReactionDAO:
    @staticmethod
    def find_by_slug_and_user(slug: str, user: User):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug, Reaction.user == user).first()
    
    @staticmethod
    def find_by_resource_id_and_user(resource_id: int, user: User):
        return Reaction.query.filter(Reaction.resource_id == resource_id, Reaction.user == user).first()

    @staticmethod
    def find_all_by_slug(slug: str):
        return Reaction.query.join(Reaction.resource).filter(Resource.slug == slug).all()
    
    @staticmethod
    def all_by_user(user: User):
        return Reaction.query.filter_by(user=user)

    @staticmethod
    def find_all_by_user(user: User):
        return ReactionDAO().all_by_user(user).all()
    
    @staticmethod
    def count_all_by_user(user: User):
        return ReactionDAO().all_by_user(user).count()
    
    # Currently unused
    @staticmethod
    def find_by_user(user: User, page=None, page_size=None):
        if page_size is None:
            return ReactionDAO().find_all_by_user(user)
        else:
            if page is None:
                page = 1
            return Reaction.query.filter_by(user=user).order_by(desc(Reaction.updated), desc(Reaction.created)).offset(
                (page - 1) * page_size).limit(page_size).all()

    # All reactions on photos
    @staticmethod
    def all_on_photos_by_user(user: User, page=None, page_size=None):
        query = Reaction.query.filter_by(user=user).filter(Reaction.gallery_type.name == GalleryTypeEnum.PHOTO.name).order_by(desc(Reaction.updated))
        return query_with_offset(query, page, page_size)

    @staticmethod
    def find_all_reactions_on_photos_by_user(user: User, page=None, page_size=None):
        all_reactions = ReactionDAO().all_on_photos_by_user(user, page, page_size).all()
        filtered_reactions = list(filter(lambda reaction: reaction.gallery_type is GalleryTypeEnum.PHOTO, all_reactions))
        return filtered_reactions
    
    @staticmethod
    def count_all_reactions_on_photos_by_user(user: User):
        return len(ReactionDAO().find_all_reactions_on_photos_by_user(user))