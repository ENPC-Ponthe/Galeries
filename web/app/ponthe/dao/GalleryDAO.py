from .ResourceDAO import ResourceDAO
from ..models import Gallery, Year, Event


class GalleryDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Gallery)

    @staticmethod
    def find_by_event_and_year_slugs(event_slug: str,  year_slug: str):
        return Gallery.query.join(Gallery.year).join(Gallery.event).filter(Year.slug == year_slug, Event.slug == event_slug).all()

    @staticmethod
    def find_public_by_year(year: Year):
        return Gallery.query.filter_by(year=year, private=False).all()

    @classmethod
    def find_private_by_year(cls, year: Year):
        galleries = Gallery.query.filter_by(year=year, private=True).all()
        return list(filter(cls.has_right_on, galleries))
