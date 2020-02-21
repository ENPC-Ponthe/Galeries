from flask_thumbnails import utils
from sqlalchemy import desc

from .ResourceDAO import ResourceDAO
from .. import app, db, thumb
from ..file_helper import delete_file
from ..filters import thumb_filter, category_thumb_filter
from ..models import File, Gallery

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']
DEFAULT_SIZE_THUMB = "226x226"


class FileDAO(ResourceDAO):
    def __init__(self):
        super().__init__(File)

    @staticmethod
    def create_thumb(file: File, size=DEFAULT_SIZE_THUMB):
        return thumb_filter(file, size)

    @staticmethod
    def get_thumb_path(file: File, size=DEFAULT_SIZE_THUMB):
        return os.path.join(THUMB_FOLDER, file.gallery.slug,
                                  utils.generate_filename(file.filename, size, "fit", "90"))

    @staticmethod
    def get_thumb_path_or_create_it(file: File, size=DEFAULT_SIZE_THUMB):
        thumb_file_path = FileDAO.get_thumb_path(file, size)
        try:
            thumbnail = open(thumb_file_path)
            thumbnail.close()
        except:
            FileDAO.create_thumb(file, size)
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
    def all_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        if page_size is None:
            files = File.query.filter_by(gallery=gallery)
        else:
            if page is None:
                page = 1
            files = File.query.filter_by(gallery=gallery).offset((page - 1) * page_size).limit(page_size)
        return files

    @staticmethod
    def find_all_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        return FileDAO.all_files_by_gallery(gallery, page, page_size).all()

    @staticmethod
    def find_not_pending_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        files = FileDAO.find_all_files_by_gallery(gallery, page, page_size)
        return list(filter(lambda file: not file.pending, files))

    @staticmethod
    def get_number_of_files_by_gallery(gallery: Gallery):
        return FileDAO.all_files_by_gallery(gallery).count()
    
    @staticmethod
    def get_number_of_not_pending_files_by_gallery(gallery: Gallery):
        return len(FileDAO.find_not_pending_files_by_gallery(gallery))