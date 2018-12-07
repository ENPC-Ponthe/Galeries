from .ResourceDAO import ResourceDAO
from .. import db
from ..models import Event


class EventDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Event)

    def delete_detaching_galleries(self, event_slug: str):
        event = self.find_by_slug(event_slug)
        for gallery in event.galleries:
            gallery.event=None
        db.session.commit()
        db.session.delete(event)
        db.session.commit()
