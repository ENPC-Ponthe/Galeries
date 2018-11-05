from flask_thumbnails import utils

from .ResourceDAO import ResourceDAO
from .. import app, db
from ..file_helper import delete_file
from ..models import File

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']

class FileDAO(ResourceDAO):
    def __init__(self):
        super().__init__(File)

    @staticmethod
    def delete(file: File):
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        thumb_file = os.path.join(THUMB_FOLDER, file.gallery.slug, utils.generate_filename(file.filename, "226x226", "fit", "90"))
        delete_file(file_path)
        delete_file(thumb_file)
        db.session.delete(file)
        db.session.commit()

    def delete_by_slug(self, slug):
        self.delete(self.find_by_slug(slug))