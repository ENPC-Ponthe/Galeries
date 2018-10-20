from .. import db
from ..models import Year


class YearDAO:
    @staticmethod
    def find_by_slug(slug: str):
        return Year.query.filter_by(slug=slug).one()

    @staticmethod
    def delete_detaching_galleries(slug):
        year = Year.query.filter_by(slug=slug).one()
        for gallery in year.galleries:
            gallery.year = None
            db.session.add(gallery)
        db.session.commit()
        db.session.delete(year)
        db.session.commit()