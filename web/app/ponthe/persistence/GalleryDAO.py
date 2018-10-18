from .FileDAO import FileDAO

from .. import db
from ..models import Gallery, Year, Event

class GalleryDAO:
    @staticmethod
    def find_by_event_and_year_slugs(event_slug: str,  year_slug: str):
        return Gallery.query.join(Gallery.year).join(Gallery.event).filter(Year.slug == year_slug, Event.slug == event_slug).all()

    @staticmethod
    def find_by_year(year: Year):
        return Gallery.query.filter_by(year=year).all()

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
