import os
import zipfile
from glob import glob
from datetime import datetime
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import moviepy.editor as mp
from PIL import Image, ExifTags

from .. import app, db
from ..dao import FileDAO, GalleryDAO
from ..models import File, User, FileTypeEnum
from ..file_helper import (
    create_folder, move_file, is_image, is_video, get_extension, get_base64_encoding, create_file_slug
)
from ..filters import thumb_filter

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
DEFAULT_SIZE_THUMB = '226x226'
VIDEO_RESOLUTIONS = ['720', '480', '360']  # Default video is uploaded as 1080p


# Tags for image metadata
EXIF_TAGS_TO_KEEP = ['DateTimeOriginal', 'DateTime', 'Artist', 'Model']
IMAGE_EXIF_TAGS = {
    val: key for key, val in ExifTags.TAGS.items() if val in EXIF_TAGS_TO_KEEP
}


def get_secure_videoname(file_slug: str, file: File, resolution='1080'):
    return secure_filename(file_slug + '_' + resolution + '.' + file.filename.rsplit('.', 1)[1].lower())


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
    def create(upload_file_path: str, filename: str, gallery_slug: str, author: User, artist=None, camera_model=None, datetime_original=None, datetime_edited=None):
        gallery = GalleryDAO().find_by_slug(gallery_slug)
        new_file = File(gallery=gallery, extension=get_extension(
            filename), author=author, pending=(not author.admin),
            artist=artist, camera_model=camera_model,
            date_time_original=datetime_original, date_time_edited=datetime_edited)

        if is_image(filename):
            new_file.type = FileTypeEnum.IMAGE
        elif is_video(filename):
            new_file.type = FileTypeEnum.VIDEO
        else:
            raise ValueError('File extension not supported')

        gallery_folder = os.path.join(UPLOAD_FOLDER, gallery_slug)
        create_folder(gallery_folder)
        # can't use os.rename to move to docker volume : OSError: [Errno 18] Invalid cross-device link
        move_file(upload_file_path, os.path.join(
            gallery_folder, new_file.filename))
        db.session.add(new_file)
        db.session.commit()
        if new_file.type == FileTypeEnum.IMAGE:
            thumb_filter(new_file)
        return new_file

    @staticmethod
    def save_photo(file: File, gallery_slug: str, user: User):
        file_slug = create_file_slug(file)
        filename = secure_filename(
            file_slug + '.' + file.filename.rsplit('.', 1)[1].lower())
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        # Get the metadata from the picture
        def get_datetime_from_dict(key):
            value = img_metadata[IMAGE_EXIF_TAGS[key]]
            value = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
            return value

        # TODO: Add metadata extraction from png and other files
        artist, camera_model, datetime_original, datetime_edited = None, None, None, None
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext == 'jpg':
            img_metadata = Image.open(save_path)._getexif()
            if IMAGE_EXIF_TAGS['Artist'] in img_metadata.keys():
                artist = img_metadata[IMAGE_EXIF_TAGS['Artist']]
            if IMAGE_EXIF_TAGS['Model'] in img_metadata.keys():
                camera_model = img_metadata[IMAGE_EXIF_TAGS['Model']]
            if IMAGE_EXIF_TAGS['DateTimeOriginal'] in img_metadata.keys():
                datetime_original = get_datetime_from_dict('DateTimeOriginal')
            if IMAGE_EXIF_TAGS['DateTime'] in img_metadata.keys():
                datetime_edited = get_datetime_from_dict('DateTime')

        FileService.create(save_path, filename, gallery_slug, user,
                           artist, camera_model, datetime_original, datetime_edited)

    @staticmethod
    def save_video_in_all_resolutions(file: File, gallery_slug: str, user: User):
        file_slug = create_file_slug(file)

        # Default uploaded video is considered as 1080p
        filename = get_secure_videoname(file_slug, file)
        original_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_file_path)
        # TODO: Add metadata extraction from videos
        saved_file = FileService.create(
            original_file_path, filename, gallery_slug, user)

        gallery_folder = os.path.join(UPLOAD_FOLDER, gallery_slug)
        original_moved_file_path = os.path.join(
            gallery_folder, saved_file.filename)

        for resolution in VIDEO_RESOLUTIONS:
            original_video = mp.VideoFileClip(original_moved_file_path)
            resized_filename = get_secure_videoname(
                saved_file.slug, file, resolution)
            resized_file_path = os.path.join(gallery_folder, resized_filename)
            video_resized = original_video.resize(width=int(resolution))
            video_resized.write_videofile(resized_file_path)

    @staticmethod
    def save_archive(file: File, gallery_slug: str, user: User):
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        # Extract images from zip
        dest_folder = '.'.join(save_path.split('.')[:-1]) + '/'
        if os.path.exists(dest_folder):
            os.removedirs(dest_folder)
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
        os.remove(save_path)

        # Save each image
        img_paths = glob(dest_folder + '**.**')
        for path in img_paths:
            filename = os.path.split(path)[-1]
            if is_image(filename):
                with open(path, 'rb') as file:
                    ext = filename.rsplit('.', 1)[-1].lower()
                    img = FileStorage(file, filename, content_type=f'image/{ext}')
                    FileService.save_photo(img, gallery_slug, user)

        os.removedirs(dest_folder)

    @staticmethod
    def get_absolute_file_path(file: File):
        return os.path.join(UPLOAD_FOLDER, file.file_path)

    @staticmethod
    def get_absolute_video_file_path(file: File, resolution='1080'):
        return os.path.join(UPLOAD_FOLDER, file.file_path_resolution(resolution=resolution))

    @classmethod
    def get_base64_encoding_full(cls, file: File):
        return get_base64_encoding(cls.get_absolute_file_path(file))

    @staticmethod
    def get_base64_encoding_thumb(file: File, size=DEFAULT_SIZE_THUMB):
        return get_base64_encoding(FileDAO.get_thumb_path_or_create_it(file, size))
