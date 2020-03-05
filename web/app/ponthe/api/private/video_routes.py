from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask import request

from . import api
from ... import app
from ...dao import GalleryDAO, FileDAO
from ...services import UserService
from ...services import FileService


SIZE_LARGE_THUMB = "630x500"


@api.route('/get-filmography')
class GetFilmography(Resource):
    @api.response(200, 'Success')
    def post(self):
        page = request.json.get("page")
        page_size = request.json.get("page_size")
        # Starting and ending year are None for admins
        starting_year, ending_year = UserService.get_user_allowed_years(current_user)

        '''Get the list of public galleries of all years'''

        public_video_galleries = GalleryDAO().find_all_public_video_sorted_by_date(page, page_size, starting_year, ending_year)
        number_of_public_video_galleries = GalleryDAO().count_all_public_video_sorted_by_date(starting_year, ending_year)

        video_galleries_data = []
        for gallery in public_video_galleries:
            gallery_data = {
                "name": gallery.name,
                "slug": gallery.slug
            }

            cover_image = FileDAO().get_cover_image_of_video_gallery(gallery)
            if cover_image is not None:
                encoded_string = FileService.get_base64_encoding_thumb(cover_image, SIZE_LARGE_THUMB)
                gallery_data["image"] = encoded_string

            video_galleries_data.append(gallery_data)

        return {
                    "number_of_videos": number_of_public_video_galleries,
                    "galleries": video_galleries_data
                }, 200


@api.route('/get-video-data')
@api.doc(params={
    'gallery_slug': 'the video gallery which owns the video you want'
})
class GetVideoData(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Request incorrect - JSON not valid')
    @api.response(403, 'Not authorized - account not valid')
    def post(self):
        '''Get information about a video which is in gallery of slug gallery_slug'''
        gallery_slug = request.json.get("gallery_slug")

        gallery = GalleryDAO().find_by_slug(gallery_slug)

        cover_image = FileDAO().get_cover_image_of_video_gallery(gallery)
        has_cover_image = cover_image is not None
        video = FileDAO().get_video_from_gallery_slug(gallery.slug)
        has_video = video is not None

        return {
            "name": gallery.name,
            "description": gallery.description,
            "private": gallery.private,
            "has_cover_image": has_cover_image,
            "has_video" = has_video
            }, 200
