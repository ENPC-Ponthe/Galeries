from .. import db
from ..models import Event, File


class EventDAO:
    @staticmethod
    def find_by_year(year):
        Event.query.filter(File.query.filter_by(year=year, event_id=Event.id).exists()).all()

    @staticmethod
    def delete_detaching_galleries(event_slug):
        event = Event.query.filter_by(slug=event_slug).one()
        for gallery in event.galleries:
            gallery.event=None
            db.session.add(gallery)
        db.session.commit()
        db.session.delete(event)
        db.session.commit()
