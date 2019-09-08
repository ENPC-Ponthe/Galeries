import os

from .. import app, db
from ..dao import FileDAO, GalleryDAO
from ..models import File, User, FileTypeEnum
from ..file_helper import create_folder, move_file, is_image, is_video, get_extension, get_base64_encoding
from ..filters import thumb_filter

UPLOAD_FOLDER = app.config['MEDIA_ROOT']


class FileService:
    @staticmethod
    def delete(file_slug: str, current_user: User):
        file = FileDAO().find_by_slug(file_slug)
        if FileDAO.has_right_on(file, current_user):
            FileDAO.delete(file)

    @staticmethod
    def approve(file: File):
        file.pending = False
        db.session.commit()

    @classmethod
    def approve_by_slug(cls, slug: str):
        file = FileDAO().find_by_slug(slug)
        cls.approve(file)

    @staticmethod
    def create(upload_file_path: str, filename: str, gallery_slug: str, author: User):
        gallery = GalleryDAO().find_by_slug(gallery_slug)
        new_file = File(gallery=gallery, extension=get_extension(filename), author=author, pending=(not author.admin))

        if is_image(filename):
            new_file.type = FileTypeEnum.IMAGE
        elif is_video(filename):
            new_file.type = FileTypeEnum.VIDEO
        else:
            raise ValueError("File extension not supported")

        gallery_folder = os.path.join(UPLOAD_FOLDER, gallery_slug)
        create_folder(gallery_folder)
        # can't use os.rename to move to docker volume : OSError: [Errno 18] Invalid cross-device link
        move_file(upload_file_path, os.path.join(gallery_folder, new_file.filename))
        db.session.add(new_file)
        db.session.commit()
        if new_file.type == FileTypeEnum.IMAGE:
            thumb_filter(new_file)

    @staticmethod
    def get_base64_encoding_full(file: File):
        return get_base64_encoding(os.path.join(UPLOAD_FOLDER, file.file_path))

    @staticmethod
    def get_base64_encoding_thumb(file: File):
        return get_base64_encoding(FileDAO.get_thumb_path_or_create_it(file))