from .. import app, db
from ..file_helper import delete_file
from ..models import File

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']

class FileDAO:
    @staticmethod
    def find_by_slug(slug):
        return File.query.filter_by(slug=slug).one()

    @staticmethod
    def delete(file: File):
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        delete_file(file_path)
        db.session.delete(file)
        db.session.commit()

    @classmethod
    def delete_by_slug(cls, slug):
        cls.delete(cls.find_by_slug(slug))