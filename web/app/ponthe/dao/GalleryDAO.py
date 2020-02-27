from sqlalchemy import desc, between

from .ResourceDAO import ResourceDAO
from ..models import Gallery, Year, Event, User


def query_with_offset(query, page=None, page_size=None):
    if page_size is None:
        return query
    else:
        if page is None:
            page = 1
        return query.offset((page - 1) * page_size).limit(page_size)


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

    # Get all public galleries
    @staticmethod
    def all_public_sorted_by_date(page=None, page_size=None, starting_year=None, ending_year=None):
        if starting_year is None and ending_year is None:
            galleries = Gallery.query.filter_by(private=False)
        elif starting_year is not None and ending_year is not None:
            galleries = Gallery.query.join(Gallery.year).filter(Gallery.private == False).filter(Year.slug >= starting_year, Year.slug <= ending_year)
        else:
            return []
        return query_with_offset(galleries.order_by(desc(Gallery.created)), page, page_size)

    @staticmethod
    def find_all_public_sorted_by_date(page=None, page_size=None, starting_year=None, ending_year=None):
        return GalleryDAO.all_public_sorted_by_date(page, page_size, starting_year, ending_year).all()
    
    @staticmethod
    def count_all_public_sorted_by_date(starting_year=None, ending_year=None):
        return GalleryDAO.all_public_sorted_by_date(starting_year=starting_year, ending_year=ending_year).count()