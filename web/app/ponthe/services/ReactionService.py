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
    def update(new_reaction_type: ReactionEnum, image_slug: str, user: User):
        current_reaction = ReactionDAO().find_by_slug_and_user(image_slug, user)
        current_reaction.type = new_reaction_type
        db.session.commit()
        return current_reaction
    
    @staticmethod
    def get_enum_reaction(reaction: str):
        return ReactionEnum[reaction].value
    
    @staticmethod
    def get_enum_reaction_name(index: int):
        return ReactionEnum(index).name

    @staticmethod
    def image_has_reaction_from_user(image_slug: str, user: User):
        reaction = ReactionDAO().find_by_slug_and_user(image_slug, user)
        if reaction is not None:
            return True
        return False
    
    @staticmethod
    def count_reactions_by_image_slug(image_slug: str):
        reactions = ReactionDAO().find_all_by_slug(slug=image_slug)
        count_reactions = {}

        for reaction in reactions:
            reaction_type = ReactionService.get_enum_reaction_name(reaction.type)
            if not reaction_type in count_reactions:
                count_reactions[reaction_type] = 1
            else:
                count_reactions[reaction_type] += 1
        return count_reactions