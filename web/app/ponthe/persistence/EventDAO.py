from .. import db
from ..models import Event, File


class EventDAO:
    @staticmethod
    def find_by_slug(slug: str):
        return Event.query.filter_by(slug=slug).one()

    @staticmethod
    def delete_detaching_galleries(event_slug):
        event = Event.query.filter_by(slug=event_slug).one()
        for gallery in event.galleries:
            gallery.event=None
            db.session.add(gallery)
        db.session.commit()
        db.session.delete(event)
        db.session.commit()
