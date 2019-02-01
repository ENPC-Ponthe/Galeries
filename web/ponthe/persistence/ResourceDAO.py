from flask_login import current_user
from ponthe.models import Resource
from sqlalchemy import desc


class ResourceDAO:
    def __init__(self, SubResource):
        self.SubResource = SubResource

    def find_by_slug(self, slug: str):
        return self.SubResource.query.filter_by(slug=slug).one()

    def find_by_id(self, id: int):
        return self.SubResource.query.filter_by(id=id).one()

    def find_all(self):
        return self.SubResource.query.all()

    def find_all_sorted_by_date(self):
        return self.SubResource.query.order_by(desc(self.SubResource.created)).limit(10).all()

    @staticmethod
    def has_right_on(resource: Resource, given_current_user = None):
        if given_current_user == None:
            return current_user.admin or current_user.id == resource.author_id
        else:
            return given_current_user.admin or given_current_user.id == resource.author_id
