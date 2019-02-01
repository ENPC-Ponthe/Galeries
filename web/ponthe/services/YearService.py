from .. import db
from ..models import User, Year

class YearService:
    @staticmethod
    def create(value: int, description:str, author: User):
        year = Year(value=value, author=author)
        if description:
            year.description = description
        db.session.add(year)
        db.session.commit()