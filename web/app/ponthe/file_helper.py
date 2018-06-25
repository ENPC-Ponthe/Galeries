import os

def is_image(filename):
    """ Renvoie True si le fichier possede une extension d'image valide. """
    return '.' in filename and filename.rsplit('.', 1)[-1] in ('png', 'jpg', 'jpeg', 'gif', 'bmp')

def is_video(filename):
    """ Renvoie True si le fichier possede une extension de vidéo valide. """
    return '.' in filename and filename.rsplit('.', 1)[-1] in ('mp4', 'avi')

def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. {}'.format(directory))

def ext(filename):
    _, extension = filename.rsplit('.', 1)
    return extension
