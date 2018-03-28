from . import db
from flask_login import UserMixin

class Admin(db.Model):

    __tablename__ = 'Admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastname = db.Column(db.String(64), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)  # type mot de passe qui gère le hashage derrière

    def __repr__(self):
        return '<Admin {0}>'.format("{} {}".format(self.firstname, self.lastname))

class User(UserMixin):
    pass

class Dossier(db.Model):

    __tablename__ = 'Dossier'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    annees = db.Column(db.Integer, db.ForeignKey('Annees.id'))
    annees_rel = db.relationship('Annees', backref='Dossiers')
    events = db.Column(db.Integer, db.ForeignKey('Events.id'))
    events_rel = db.relationship('Events', backref='Dossiers')  # plusieurs Dossiers peuvent appartenir à l'event Campagne BDE mais d'années différentes
    filename = db.Column(db.String(64), unique=True, nullable=False)
    couv = db.Column(db.Boolean(), nullable=False) # photo de couverture du dossier
    cat = db.Column(db.String(64), nullable=False)  # 'sport', 'evenement', 'vie-associative', 'soiree'

    def __repr__(self):
        return '<Dossier {0}>'.format(self.filename)

class Events(db.Model):

    __tablename__ = 'Events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    events = db.Column(db.String(64), nullable=False)   # nom de l'event Campagne BDE qui peut être sur plusieurs années

    def __repr__(self):
        return '<Event {0}>'.format(self.name)

class Annees(db.Model):

    __tablename__ = 'Annees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    annees = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Annee {0}>'.format(self.value)

#Dossier: annees events filename couv cat

#Admin: id, lastname fistname email password

#Events: events

#Annees: annees
