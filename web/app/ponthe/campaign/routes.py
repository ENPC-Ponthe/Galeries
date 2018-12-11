from .. import jwt
from . import campaign
from .dao import ListeDAO
from .schema import listes_schema, hotlines_schema


@campaign.route('/listes')
def listes():
    listes = ListeDAO.find_all()

    return listes_schema.jsonify(listes)


@campaign.route('/listes/<liste_id>/hotlines')
def hotlines(liste_id):
    hotlines = ListeDAO.find_by_slug(liste_id).hotlines

    return hotlines_schema.jsonify(hotlines)

