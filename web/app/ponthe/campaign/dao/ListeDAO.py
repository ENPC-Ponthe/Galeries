from typing import List
from ..models import Liste


class ListeDAO():
    @staticmethod
    def find_by_slug(slug: str) -> Liste:
        return Liste.query.filter_by(slug=slug).one()

    @staticmethod
    def find_all() -> List[Liste]:
        return Liste.query.all()
