from . import app, thumb
from .models import FileTypeEnum, File

DEFAULT_SIZE_THUMB="226x226"

@app.template_filter('thumb')
def thumb_filter(file: File, size=DEFAULT_SIZE_THUMB):
    return thumb.get_thumbnail(file.file_path, size)


@app.template_filter('category_thumb')
def category_thumb_filter(file: File):
    return thumb.get_thumbnail(file.file_path, '630x500')


@app.template_filter('is_image')
def is_image_filter(file: File):
    return file.type == FileTypeEnum.IMAGE


@app.template_filter('is_video')
def is_video_filter(file: File):
    return file.type == FileTypeEnum.VIDEO
