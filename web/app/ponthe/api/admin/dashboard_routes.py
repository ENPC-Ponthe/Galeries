from flask_restplus import Resource
from flask import request
from werkzeug.exceptions import BadRequest

from . import api
from ...services import UserService, AssetService


@api.route('/import-users')
@api.doc(params={
    'csv': 'csv file in form-data body'
})
class ImportUsers(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - Form-data not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        if 'csv' in request.files:
            file = request.files['csv']
        else:
            raise BadRequest('No CSV uploaded')

        UserService.create_users(file)


@api.route('/edit-cgu')
@api.response(200, 'Success')
@api.doc(params={
    'cgu': 'json with the new cgus'
})
class EditCgu(Resource):
    def post(self):
        new_cgu = request.json.get('cgu')
        AssetService.edit_cgu(new_cgu)
        
        response = {'msg': 'success'}
        return response, 200


@api.route('/edit-members')
@api.response(200, 'Success')
@api.doc(params={
    'members': 'json with the new members'
})
class EditMembers(Resource):
    def post(self):
        new_members = request.json.get('members')
        AssetService.edit_members(new_members)
        
        response = {'msg': 'success'}
        return response, 200


@api.route('/useful-links')
class GetUsefulLinks(Resource):
    def get(self):
        useful_links = AssetService.get_useful_links()
        return useful_links, 200


@api.route('/edit-useful-links')
@api.response(200, 'Success')
@api.doc(params={
    'links': 'json with the new useful links'
})
class EditUsefulLinks(Resource):
    def post(self):
        new_useful_links = request.json.get('links')
        AssetService.edit_useful_links(new_useful_links)

        response = {'msg': 'success'}
        return response, 200


@api.route('/admin-tutorials')
class GetAdminTutorials(Resource):
    def get(self):
        admin_tutorials = AssetService.get_admin_tutorials()
        return admin_tutorials, 200


@api.route('/edit-admin-tutorials')
@api.response(200, 'Success')
@api.doc(params={
    'tutorials': 'json with the new admin tutorials'
})
class EditAdminTutorials(Resource):
    def post(self):
        new_admin_tutorials = request.json.get('tutorials')
        AssetService.edit_admin_tutorials(new_admin_tutorials)

        response = {'msg': 'success'}
        return response, 200
