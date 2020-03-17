import os
import json

from flask_restplus import Resource

from . import api
from ... import app


ASSET_FOLDER = app.config['ASSET_ROOT']


@api.route('/members')
class Members(Resource):
    def get(self):
        '''Get Ponthe members'''
        with open(os.path.join(ASSET_FOLDER, "data/members.json")) as members:
            return json.load(members, strict=False)
