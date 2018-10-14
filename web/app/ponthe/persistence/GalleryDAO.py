from ..models import Gallery, Year, Event


class GalleryDAO:
    @staticmethod
    def find_by_event_and_year_slugs(event_slug,  year_slug):
        return Gallery.query.join(Gallery.year).join(Gallery.event).filter(Year.slug == year_slug, Event.slug == event_slug).all()

    @staticmethod
    def find_by_year(year):
        return Gallery.query.filter_by(year=year).all()
