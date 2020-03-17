import os
from typing import List

from .. import app, db
from ..dao import FileDAO, ReactionDAO
from ..models import User, ReactionEnum, Reaction
from ..services import FileService


SIZE_LARGE_THUMB = "630x500"


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
    
    @staticmethod
    def delete(image_slug: str, user: User):
        reaction = ReactionDAO().find_by_slug_and_user(image_slug, user)
        db.session.delete(reaction)
        db.session.commit()
    
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

    @staticmethod
    def get_user_reaction_type_by_slug(slug: str, user: User):
        own_reaction = ReactionDAO().find_by_slug_and_user(slug, user)
        if own_reaction is not None:
            own_reaction_type = ReactionService.get_enum_reaction_name(own_reaction.type)
        else :
            own_reaction_type = None
        return own_reaction_type


    @staticmethod
    def format_reaction_to_json(reaction: Reaction):
        reaction_type = ReactionService.get_enum_reaction_name(reaction.type)
        file = reaction.resource
        encoded_string = FileService.get_base64_encoding_thumb(file, SIZE_LARGE_THUMB)
        all_reactions_for_file = ReactionService.count_reactions_by_image_slug(file.slug)
        gallery_of_file = file.gallery
        return {
            "own_reaction": reaction_type,
            "all_reactions": all_reactions_for_file,
            "name": gallery_of_file.name,
            "file_path": file.file_path,
            "image": encoded_string
        }
    
    @staticmethod
    def format_reactions_to_json(reactions: List[Reaction]):
        list_of_reactions = []
        for reaction in reactions:
            list_of_reactions.append(ReactionService.format_reaction_to_json(reaction))
        return list_of_reactions