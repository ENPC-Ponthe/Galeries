from .. import db
from ..models import Event, User
from ..persistence import CategoryDAO

class EventService():
    @staticmethod
    def create(name: str, description: str, category_slug: str, author: User):
        event = Event(name=name, author=author)
        if category_slug:
            event.category = CategoryDAO().find_by_slug(category_slug)
        if description:
            event.description = description
        db.session.add(event)
        db.session.commit()