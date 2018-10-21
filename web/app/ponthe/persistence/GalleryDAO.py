import os

from flask_login import current_user

from .FileDAO import FileDAO
from .. import app, db
from ..models import Gallery, Year, Event
from ..file_helper import delete_folder

UPLOAD_FOLDER = app.config['MEDIA_ROOT']

class GalleryDAO:
    @staticmethod
    def find_by_event_and_year_slugs(event_slug: str,  year_slug: str):
        return Gallery.query.join(Gallery.year).join(Gallery.event).filter(Year.slug == year_slug, Event.slug == event_slug).all()

    @staticmethod
    def find_public_by_year(year: Year):
        return Gallery.query.filter_by(year=year, private=False).all()

    @staticmethod
    def find_by_slug(slug: str):
        return Gallery.query.filter_by(slug=slug).one()

    @staticmethod
    def delete(gallery_slug: str):
        gallery = Gallery.query.filter_by(slug=gallery_slug).one()
        for file in gallery.files:
            FileDAO.delete(file)
        db.session.delete(gallery)
        db.session.commit()
        delete_folder(os.path.join(UPLOAD_FOLDER, gallery_slug))

    @classmethod
    def make_private(cls, slug):
        gallery = cls.find_by_slug(slug)
        if current_user.admin or current_user.id == gallery.author_id:
            gallery.private = True
            db.session.add(gallery)
            db.session.commit()

    @classmethod
    def make_public(cls, slug):
        gallery = GalleryDAO.find_by_slug(slug)
        if current_user.admin or current_user.id == gallery.author_id:
            gallery.private = False
            db.session.add(gallery)
            db.session.commit()