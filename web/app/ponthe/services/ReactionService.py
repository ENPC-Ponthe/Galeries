import os

from .. import app, db
from ..dao import FileDAO, ReactionDAO
from ..models import User, ReactionEnum, Reaction

class ReactionService():
    @staticmethod
    def create(reaction: ReactionEnum, image_slug: str, user: User):
        resource = FileDAO().find_by_slug(image_slug)
        new_reaction = Reaction(user=user, resource=resource, type=reaction)
        
        db.session.add(new_reaction)
        db.session.commit()

    @staticmethod
    def update(reaction: ReactionEnum, image_slug: str, user: User):
        resource = FileDAO().find_by_slug(image_slug)
        reaction = Reaction.query.filter(Reaction.resource == resource, Reaction.user == user)
        reaction.type = reaction
        db.session.commit()
    
    @staticmethod
    def get_enum_reaction(reaction: str):
        return ReactionEnum[reaction].value

    @staticmethod
    def image_has_reaction_from_user(image_slug: str, user: User):
        reaction = ReactionDAO().find_by_slug_and_user(image_slug, user)
        if reaction is not None:
            return True
        return False