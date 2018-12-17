from flask import url_for
from ..models import Gallery

from ...views import thumb_filter, mobile_thumb_filter
from ... import ma


class ImageSourceSchema(ma.Schema):
    class Meta:
        fields = ('uri', 'id', 'thumbnail', 'name')

    uri = ma.Function(lambda file: url_for('api.uploads', file_path=file.file_path))
    thumbnail = ma.Function(lambda file: mobile_thumb_filter(file))


class GallerySchema(ma.Schema):
    class Meta:
        model = Gallery
    files = ma.List(ma.Nested(ImageSourceSchema()))
    cover_uri = ma.Function(lambda gallery: thumb_filter(gallery.cover))


gallery_schema = GallerySchema(only=['name', 'description', 'files'])
galleries_schema = GallerySchema(many=True, only=['name', 'slug', 'cover_uri'])
