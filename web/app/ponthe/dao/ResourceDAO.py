from ..models import Resource, User


class ResourceDAO:
    def __init__(self, SubResource):
        self.SubResource = SubResource

    def find_by_slug(self, slug: str):
        return self.SubResource.query.filter_by(slug=slug).one()

    def find_by_id(self, id: int):
        return self.SubResource.query.get(id)

    def find_all(self):
        return self.SubResource.query.all()

    @staticmethod
    def has_right_on(resource: Resource, current_user: User):
        return current_user.admin or current_user.id == resource.author_id
