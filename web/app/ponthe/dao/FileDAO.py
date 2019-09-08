from flask_thumbnails import utils
from sqlalchemy import desc

from .ResourceDAO import ResourceDAO
from .. import app, db, thumb
from ..file_helper import delete_file
from ..filters import thumb_filter
from ..models import File, Gallery

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']


class FileDAO(ResourceDAO):
    def __init__(self):
        super().__init__(File)

    @staticmethod
    def create_thumb(file: File):
        return thumb_filter(file)

    @staticmethod
    def get_thumb_path(file: File):
        return os.path.join(THUMB_FOLDER, file.gallery.slug,
                                  utils.generate_filename(file.filename, "226x226", "fit", "90"))

    @classmethod
    def get_thumb_path_or_create_it(cls, file: File):
        thumb_file_path = cls.get_thumb_path(file)
        try:
            thumbnail = open(thumb_file_path)
            thumbnail.close()
        except:
            cls.create_thumb(file)
        return thumb_file_path

    @classmethod
    def delete(cls, file: File):
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        thumb_file_path = cls.get_thumb_path(file)
        delete_file(file_path)
        delete_file(thumb_file_path)
        db.session.delete(file)
        db.session.commit()

    def delete_by_slug(self, slug: str):
        self.delete(self.find_by_slug(slug))

    @staticmethod
    def find_all_moderated_sorted_by_date(page: int, page_size: int):
        return File.query.filter_by(pending=False).order_by(desc(File.created)).offset((page-1)*page_size).limit(page_size).all()

    @staticmethod
    def find_all_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        if page_size is None:
            files = File.query.filter_by(gallery=gallery).all()
        else:
            if page is None:
                page = 1
            files = File.query.filter_by(gallery=gallery).offset((page - 1) * page_size).limit(page_size).all()
        return files

    @staticmethod
    def find_not_pending_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        files = FileDAO.find_all_files_by_gallery(gallery, page, page_size)
        return list(filter(lambda file: not file.pending, files))
