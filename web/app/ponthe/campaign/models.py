from .. import db
from ..config import Constants
import enum


class ListeType(enum.Enum):
    BDE = 1
    BDS = 2
    BDA = 3


class Liste(db.Model):
    __tablename__ = 'listes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    promotion = db.Column(db.String(64), nullable=False)    # in .config.Constants.AVAILABLE_PROMOTIONS
    type = db.Column(db.String(64), nullable=False)
    gallery_id = db.Column(db.Integer, db.ForeignKey('galleries.id', name='fk_liste_gallery'))
    gallery = db.relationship('Gallery', backref='liste', foreign_keys=[gallery_id], uselist=False)

    def __init__(self, name, type):
        self.name = name
        self.promotion = Constants.AVAILABLE_PROMOTIONS[-1]
        self.type = type


class Hotline(db.Model):
    __tablename__ = 'hotlines'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(10))
    image_url = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    liste_id = db.Column(db.Integer, db.ForeignKey('listes.id', name='fk_hotlines_liste'), nullable=False)
    liste = db.relationship('Liste', backref='hotlines', foreign_keys=[liste_id])
