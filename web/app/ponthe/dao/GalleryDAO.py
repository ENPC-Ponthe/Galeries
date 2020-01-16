from sqlalchemy import desc

from .ResourceDAO import ResourceDAO
from ..models import Gallery, Year, Event, User


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
    def find_private_by_year(cls, year: Year, current_user: User):
        galleries = Gallery.query.filter_by(year=year, private=True).all()
        return list(filter(lambda gallery: cls.has_right_on(gallery, current_user), galleries))

    @staticmethod
    def find_public():
        return Gallery.query.filter_by(private=False).all()

    @staticmethod
    def find_private():
        return Gallery.query.filter_by(private=True).all()

    @staticmethod
    def find_public_sorted_by_date(page, page_size):
        return Gallery.query.filter_by(private=False).order_by(desc(Gallery.created)).offset(
            (page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def find_all_public_sorted_by_date():
        return Gallery.query.filter_by(private=False).order_by(desc(Gallery.created)).all()

    # Test
    @staticmethod
    def find_all_public_sorted_by_date_filtered_by_years(beginning_year, ending_year):
        return Gallery.query.filter_by(private=False, year>=beginning_year, year<=ending_year).order_by(desc(Gallery.created)).all()
