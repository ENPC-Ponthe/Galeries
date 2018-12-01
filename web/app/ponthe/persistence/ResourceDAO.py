from flask_login import current_user
from ponthe.models import Resource


class ResourceDAO:
    def __init__(self, SubResource):
        self.SubResource = SubResource

    def find_by_slug(self, slug: str):
        return self.SubResource.query.filter_by(slug=slug).one()

    def find_all(self):
        return self.SubResource.query.all()

    @staticmethod
    def has_right_on(resource: Resource):
        return current_user.admin or current_user.id == resource.author_id
