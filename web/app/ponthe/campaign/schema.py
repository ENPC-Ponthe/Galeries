from .. import ma
from .models import Hotline


class ListeSchema(ma.Schema):
    class Meta:
        # model = Liste
        fields = ('name', 'type', 'hotlines')


class HotlineSchema(ma.Schema):
    class Meta:
        model = Hotline

listes_schema = ListeSchema(many=True)
hotlines_schema = HotlineSchema(many=True)