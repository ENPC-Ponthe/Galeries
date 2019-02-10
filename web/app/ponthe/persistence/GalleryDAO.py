from .ResourceDAO import ResourceDAO
from ..models import Gallery, Year, Event
from sqlalchemy import desc

class GalleryDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Gallery)

    @staticmethod
    def find_by_event_and_year_slugs(event_slug: str,  year_slug: str):
        return Gallery.query.join(Gallery.year).join(Gallery.event).filter(Year.slug == year_slug, Event.slug == event_slug).all()

    @staticmethod
    def find_public_by_year(year: Year):
        return Gallery.query.filter_by(year=year, private=False).all()
    @staticmethod
    def find_all_public():
        return Gallery.query.filter_by(private=False).all()

    @staticmethod
    def find_all_sorted_by_date(page, page_size):
        return Gallery.query.order_by(desc(Gallery.created)).offset((page-1)*page_size).limit(page_size).all()

    @classmethod
    def find_private_by_year(cls, year: Year):
        galleries = Gallery.query.filter_by(year=year, private=True).all()
        return list(filter(cls.has_right_on, galleries))
