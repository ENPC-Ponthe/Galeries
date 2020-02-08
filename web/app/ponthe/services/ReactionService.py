import os

from .. import app, db
from ..dao import ResourceDAO
from ..models import User, ReactionEnum

class ReactionService:
    @staticmethod
    def create(reaction: ReactionEnum, image_slug: str, user: User):
        resource = ResourceDAO.find_by_slug(image_slug)
        new_reaction = Reaction(user=user, resource=resource, type=reaction)
        
        db.session.add(new_reaction)
        db.session.commit()

    @staticmethod
    def update(reaction: ReactionEnum, image_slug: str, user: User):
        reaction = Reaction.query.filter(Reaction.resource == image_slug, Reaction.user == user)
        reaction.type = reaction
        db.session.commit()
    
    @staticmethod
    def get_enum_reaction(reaction: str):
        return ReactionEnum[reaction].value