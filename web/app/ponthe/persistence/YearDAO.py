from .. import db
from ..models import Year


class YearDAO:
    @staticmethod
    def delete_detaching_galleries(year_slug):
        year = Year.query.filter_by(slug=year_slug).one()
        for gallery in year.galleries:
            gallery.year = None
            db.session.add(gallery)
        db.session.commit()
        db.session.delete(year)
        db.session.commit()