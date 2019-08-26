from flask_thumbnails import utils
from sqlalchemy import desc

from .ResourceDAO import ResourceDAO
from .. import app, db
from ..file_helper import delete_file
from ..models import File, Gallery

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']


class FileDAO(ResourceDAO):
    def __init__(self):
        super().__init__(File)

    @staticmethod
    def delete(file: File):
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        thumb_file = os.path.join(THUMB_FOLDER, file.gallery.slug,
                                  utils.generate_filename(file.filename, "226x226", "fit", "90"))
        delete_file(file_path)
        delete_file(thumb_file)
        db.session.delete(file)
        db.session.commit()

    def delete_by_slug(self, slug: str):
        self.delete(self.find_by_slug(slug))

    def find_all_moderated_sorted_by_date(self, page: int, page_size: int):
        return File.query.filter_by(pending=False).order_by(desc(File.created)).offset((page-1)*page_size).limit(page_size).all()

    @staticmethod
    def find_all_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        if page_size == None:
            files = File.query.filter_by(gallery=gallery).all()
        else:
            if page == None:
                page = 1
            files = File.query.filter_by(gallery=gallery).offset((page - 1) * page_size).limit(page_size).all()
        return files

    @staticmethod
    def find_not_pending_files_by_gallery(gallery: Gallery, page=None, page_size=None):
        files = FileDAO.find_all_files_by_gallery(gallery, page, page_size)
        return list(filter(lambda file: not file.pending, files))
