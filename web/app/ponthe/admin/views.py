from . import admin
import os
from ..models import Year, Event, File, User
from .. import db
from flask_login import current_user, login_required
from ..file_helper import create_folder, is_image, is_video, ext

@admin.before_request     # login en tant qu'admin nécessaire pour tout le blueprint
@login_required
def before_request():
    if not current_user.admin:
        abort(401)

def batch_upload():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("../../instance/club_folder")
    user_ponthe = User.query.filter_by(username="ponthe.enpc").one()    # Utilisateur à créer au déploiement du site

    for dirname in os.listdir("waiting_zone"):
        year = Year.query.filter_by(value=dirname).first()
        if year is None:
            year = Year(value=dirname)
            db.session.add(year)
            create_folder(os.path.join("uploads", dirname))
        for subdirname in os.listdir(os.path.join("waiting_zone", dirname)):
            event = Event.query.filter_by(name=subdirname).first()
            if event is None:
                event = Event(name=subdirname)
                db.session.add(event)
                create_folder(os.path.join("uploads", dirname, subdirname))
            for filename in os.listdir(os.path.join("waiting_zone", dirname, subdirname)):
                new_file = File(year=year, event=event, extension=ext(filename), author=user_ponthe, pending=False)
                if is_image(filename):
                    new_file.type = "IMAGE"
                elif is_video(filename):
                    new_file.type = "VIDEO"
                else:
                    raise ValueError("File extension not supported")
                os.rename(os.path.join("waiting_zone", dirname, subdirname, filename), os.path.join("uploads", dirname, subdirname, new_file.filename))
                db.session.add(new_file)
                db.session.commit()
