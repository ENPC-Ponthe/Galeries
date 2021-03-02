from flask_restplus import Resource

from . import api
from ...services import AssetService


@api.route('/members')
class Members(Resource):
    def get(self):
        '''Get Ponthe members'''
        members = AssetService.get_members()
        return members, 200
