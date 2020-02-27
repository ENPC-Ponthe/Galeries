from flask_thumbnails import utils
from sqlalchemy import desc

from .ResourceDAO import ResourceDAO
from .. import app, db, thumb
from ..file_helper import delete_file
from ..filters import thumb_filter, category_thumb_filter
from ..models import File, Gallery, FileTypeEnum, Year

import os

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
THUMB_FOLDER = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']
DEFAULT_SIZE_THUMB = "226x226"


def query_with_offset(query, page=None, page_size=None):
    if page_size is None:
        return query
    else:
        if page is None:
            page = 1
        return query.offset((page - 1) * page_size).limit(page_size)


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
    def get_video_path(file: File):
        return os.path.join(UPLOAD_FOLDER, file.filename)

    @classmethod
    def get_thumb_path_or_create_it(cls, file: File, size=DEFAULT_SIZE_THUMB):
        thumb_file_path = cls.get_thumb_path(file, size)
        try:
            thumbnail = open(thumb_file_path)
            thumbnail.close()
        except:
            cls.create_thumb(file, size)
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
        files = File.query.filter_by(gallery=gallery)
        return query_with_offset(files, page, page_size)

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

    # Videos
    @staticmethod
    def all_public_videos(page=None, page_size=None, starting_year=None, ending_year=None):
        if starting_year is None and ending_year is None:
            files = File.query.join(File.gallery).filter(File.type == FileTypeEnum.VIDEO.name, Gallery.private == False)
        elif starting_year is not None and ending_year is not None:
            files = File.query.join(File.gallery).join(Gallery.year).filter(File.type == FileTypeEnum.VIDEO.name, Gallery.private == False).filter(Year.slug >= starting_year, Year.slug <= ending_year)
        else :
            return []
        return query_with_offset(files, page, page_size)
    
    @staticmethod
    def find_all_public_videos(page, page_size, starting_year=None, ending_year=None):
        return FileDAO().all_public_videos(page, page_size, starting_year, ending_year).all()
    
    @staticmethod
    def count_all_public_videos(starting_year=None, ending_year=None):
        return FileDAO().all_public_videos(starting_year=starting_year, ending_year=ending_year).count()

    @staticmethod
    def get_cover_image_of_video_gallery(gallery: Gallery):
        return File.query.filter_by(gallery=gallery, type=FileTypeEnum.IMAGE.name).first()

    @staticmethod
    def get_video_from_gallery_slug(gallery_slug: str):
        return File.query.join(File.gallery).filter(Gallery.slug == gallery_slug, File.type == FileTypeEnum.VIDEO.name).first()
