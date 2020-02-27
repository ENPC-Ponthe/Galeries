import re
import os
import datetime
import json

from flask_restplus import Resource
from flask import request, redirect, send_file
from itsdangerous import SignatureExpired, BadSignature

from . import api
from ... import db, app
from ...services import FileService
from ...dao import FileDAO


ASSET_FOLDER = app.config['ASSET_ROOT']



@api.route('/get-video')
@api.doc(params={
    'image_slug': 'the image you want to get the list of reactions'
})
class GetVideo(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def get(self):
        '''Get a set of all reactions for a given image_slug'''
        # image_slug = request.json.get("image_slug")
        video = FileDAO.get_video()

        return send_file(
            open(FileService.get_absolute_file_path(video), "rb"),
            mimetype='video/mp4'
            )