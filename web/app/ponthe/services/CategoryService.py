from .. import db
from ..models import Category, User


class CategoryService():
    @staticmethod
    def create(name: str, description: str, author: User):
        category = Category(description=description, name=name, author=author)
        if description:
            category.description = description
        db.session.add(category)
        db.session.commit()
