from .. import app, db
from ..file_helper import delete_file
from ..models import File

import os

UPLOAD_FOLDER = os.path.join(app.instance_path, 'club_folder', 'uploads')


class FileDAO:
    @staticmethod
    def delete(file: File):
        file_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        delete_file(file_path)
        db.session.delete(file)
        db.session.commit()