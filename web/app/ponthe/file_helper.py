import base64
import os, shutil
from ponthe import app


def is_image(filename: str) -> bool:
    """ Renvoie True si le fichier possede une extension d'image valide. """
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ('png', 'jpg', 'jpeg', 'gif', 'bmp')


def is_video(filename: str) -> bool:
    """ Renvoie True si le fichier possede une extension de video valide. """
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ('mp4', 'avi', 'mov')


def is_allowed_file(filename: str) -> bool:
    return is_image(filename) or is_video(filename)


def create_folder(directory: str):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        app.logger.error('Error: Creating directory. {}'.format(directory))


def delete_folder(directory: str):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    except OSError:
        print('Error: Deleting directory. {}'.format(directory))


def delete_folders_in_folder(directory: str):
    for inner_directory in os.listdir(directory):
        inner_directory_path = os.path.join(directory, inner_directory)
        delete_folder(inner_directory_path)


def copy_folders_in_folder(src: str, dest: str):
    for inner_directory in os.listdir(src):
        inner_src_path = os.path.join(src, inner_directory)
        inner_dest_path = os.path.join(dest, inner_directory)
        copy_folder(inner_src_path, inner_dest_path)


def copy_folder(src: str, dest: str):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)


def copy_file(src: str, dest: str):
    try:
        shutil.copy(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('File not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('File not copied. Error: %s' % e)


def move_file(src: str, dest: str):
    try:
        shutil.move(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('File not moved. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('File not moved. Error: %s' % e)


def delete_file(file_path: str):
    try:
        os.remove(file_path)
    except OSError:
        print('Error: Deleting file. {}'.format(file_path))


def split_filename(filename: str):
    slug, extension = filename.rsplit('.', 1)
    return slug, extension


def get_extension(filename: str):
    return split_filename(filename)[1]

def get_base64_encoding(file_path: str):
    with open(file_path, "rb") as image_file:
        return "data:image/" + get_extension(file_path) + ";base64," + str(base64.b64encode(image_file.read()).decode('utf-8'))
