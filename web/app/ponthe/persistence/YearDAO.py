from .ResourceDAO import ResourceDAO
from .. import db
from ..models import Year


class YearDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Year)

    def delete_detaching_galleries(self, slug):
        year = self.find_by_slug(slug)
        for gallery in year.galleries:
            gallery.year = None
        db.session.commit()
        db.session.delete(year)
        db.session.commit()

    @staticmethod
    def find_all_ordered_by_value():
        return Year.query.order_by(Year.value).all()
