from .. import db
from ..models import Category, User
from ..persistence import CategoryDAO

class CategoryService():

    @staticmethod
    def create(name: str, description: str, author: User):
        cat = Category(description=description, name=name, author=author)
        if description:
            cat.description = description
        db.session.add(cat)
        db.session.commit()
