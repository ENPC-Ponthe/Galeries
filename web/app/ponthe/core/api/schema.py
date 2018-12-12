from flask import url_for

from ...views import thumb_filter
from ... import ma


class ImageSourceSchema(ma.Schema):
    class Meta:
        fields = ('uri', 'id', 'thumbnail', 'name')

    uri = ma.Function(lambda file: url_for('api.uploads', file_path=file.file_path))
    thumbnail = ma.Function(lambda file: thumb_filter(file))


class GallerySchema(ma.Schema):
    class Meta:
        fields = ('files', 'name', 'description')
    files = ma.List(ma.Nested(ImageSourceSchema()))


gallery_schema = GallerySchema()
