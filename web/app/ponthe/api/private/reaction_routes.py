import random

from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask import request

from . import api
from ...dao import ReactionDAO
from ...services import ReactionService


@api.route('/update-reaction')
@api.doc(params={
    'reaction': 'your reaction on a picture',
    'image_slug': 'the image you reacted to'
})
class UpdateReaction(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Create, update or delete a reaction on a picture'''
        reaction = request.json.get('reaction')
        image_slug = request.json.get('image_slug')

        if reaction == "NONE":
            ReactionService.delete(image_slug, current_user)
        elif ReactionService.image_has_reaction_from_user(image_slug, current_user):
            ReactionService.update(reaction, image_slug, current_user)
        else:
            ReactionService.create(reaction, image_slug, current_user)

        return {
            "msg": "Réaction enregistrée !",
            "reaction": reaction,
        }, 200


@api.route('/get-all-user-reactions')
class GetAllUserReactions(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Get all the pictures the user reacted to'''
        page = request.json.get("page")
        page_size = request.json.get("page_size")

        reactions = ReactionDAO().find_all_reactions_on_photos_by_user(current_user, page, page_size)
        number_of_reactions = ReactionDAO().count_all_reactions_on_photos_by_user(current_user)

        list_of_reactions = ReactionService.format_reactions_to_json(reactions)

        return {
            "number_of_reactions": number_of_reactions,
            "reactions": list_of_reactions
        }, 200


@api.route('/get-random-user-reactions')
@api.doc(params={
    'number_of_pics': 'the number of pics with reactions you want'
})
class GetRandomUserReactions(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Get random pictures among those the user reacted to'''
        number_of_pics = request.json.get("number_of_pics")

        all_reactions = ReactionDAO().find_all_reactions_on_photos_by_user(current_user)
        list_of_reactions = list(all_reactions)

        if number_of_pics > len(list_of_reactions):
            reactions = all_reactions
        else:
            resource_ids = list(map(lambda reaction: reaction.resource_id, all_reactions))
            reactions = []
            for pic in range(number_of_pics):
                i = random.randint(0, len(resource_ids) - 1)
                reaction = ReactionDAO().find_by_resource_id_and_user(resource_ids[i], current_user)
                reactions.append(reaction)
                del resource_ids[i]

        response_reactions = ReactionService.format_reactions_to_json(reactions)

        return {
            "reactions": response_reactions
        }, 200
