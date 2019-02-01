from ponthe.models import Category

from .ResourceDAO import ResourceDAO

class CategoryDAO(ResourceDAO):
    def __init__(self):
        super().__init__(Category)