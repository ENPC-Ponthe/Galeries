from ..models import Category


class CategoryDAO:
    @staticmethod
    def find_by_slug(slug):
        return Category.query.filter_by(slug=slug).one()