from flask_login import UserMixin
from datetime import datetime
import enum
from . import db

class ReactionEnum(enum.Enum):
    LIKE = 1
    DISLIKE = 2
    LOVE = 3
    HAPPY = 4
    SAD = 5

class FileTypeEnum(enum.Enum):
    IMAGE = 1
    VIDEO = 2

# See http://flask-sqlalchemy.pocoo.org/2.3/models/#many-to-many-relationships for query usage about many-to-many ralations
membership = db.Table('membership',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)  # type mot de passe qui gère le hashage derrière
    email = db.Column(db.String(64), unique=True, nullable=False)
    groups = db.relationship('Group', secondary=membership, lazy='subquery', backref=db.backref('members', lazy=True))

    def __repr__(self):
        return '<User {} {}>'.format(self.firstname, self.lastname)

class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Resource(TimestampMixin, db.Model):
    # __abstract__ = True
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_resources_user'))
    author = db.relationship('User', backref='resources', foreign_keys=[author_id])
    resource_type =  db.Column(db.String(64), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'resources',
        'polymorphic_on': resource_type
    }

    def __repr__(self):
        return '<Resource {}>'.format(self.name)

class Group(Resource):
    __tablename__ = 'groups'
    __mapper_args__ = {
        'polymorphic_identity': 'group'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    # à généraliser en galleries accessibles qui appartiennent à un (event, year)
    year_id = db.Column(db.Integer, db.ForeignKey('years.id'), nullable=True)
    year = db.relationship('Year', backref='groups', foreign_keys=[year_id])
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    event = db.relationship('Event', backref='groups', foreign_keys=[event_id])
    # pour les évenement d'attribut private = True

class Reaction(TimestampMixin, db.Model):   # relation many-to-many type Slack
    __tablename__ = 'reactions'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_reactions_user'), primary_key=True)
    user = db.relationship('User', backref='reactions', foreign_keys=[user_id])
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', name='fk_reactions_resource'), primary_key=True)
    resource = db.relationship('Resource', backref='reactions', foreign_keys=[resource_id])
    type = db.Column(db.Enum(ReactionEnum), nullable=False)

class Comment(Resource):
    __tablename__ = 'comments'
    __mapper_args__ = {
        'polymorphic_identity': 'comment'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', name='fk_comments_resource'))
    resource = db.relationship('Resource', backref='comments', foreign_keys=[resource_id])

    __mapper_args__ = {
        "inherit_condition": id == Resource.id
    }

    def __repr__(self):
        return '<Comment {}>'.format(self.id)

class Category(Resource):
    __tablename__ = 'categories'
    __mapper_args__ = {
        'polymorphic_identity': 'category'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    description = db.Column(db.String(1024), nullable=False)
    cover_image_id = db.Column(db.Integer, db.ForeignKey('files.id', name='fk_categories_file'), nullable=True)
    cover_image = db.relationship('File', backref='categories', foreign_keys=[cover_image_id])

class Event(Resource):
    __tablename__ = 'events'
    __mapper_args__ = {
        'polymorphic_identity': 'event'
    }
    # exemple de nom de l'event : Campagne BDE qui peut être sur plusieurs années

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', name='fk_events_category'), nullable=False)
    category = db.relationship('Category', backref='events', foreign_keys=[category_id])
    # dépendance circulaire entre table à migrer séparemment
    cover_image_id = db.Column(db.Integer, db.ForeignKey('files.id', name='fk_events_file'), nullable=True)
    cover_image = db.relationship('File', backref='events', foreign_keys=[cover_image_id])
    private = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Event {}>'.format(self.name)

class Year(Resource):
    __tablename__ = 'years'

    __mapper_args__ = {
        'polymorphic_identity': 'year'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    cover_image_id = db.Column(db.Integer, db.ForeignKey('files.id', name='fk_years_file'), nullable=True)
    cover_image = db.relationship('File', backref='years', foreign_keys=[cover_image_id])

    def __repr__(self):
        return '<Year {}>'.format(self.value)

file_tag = db.Table('file_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', name='fk_file_tags_tag'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id', name='fk_file_tags_file'), primary_key=True)
)

class File(Resource):
    __tablename__ = 'files'
    __mapper_args__ = {
        'polymorphic_identity': 'file'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    type = db.Column(db.Enum(FileTypeEnum), nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('years.id', name='fk_files_year'), nullable=True)
    year = db.relationship('Year', backref='files', foreign_keys=[year_id])
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', name='fk_files_event'), nullable=True)
    event = db.relationship('Event', backref='files', foreign_keys=[event_id])  # plusieurs files peuvent appartenir à l'event Campagne BDE mais d'années différentes
    filename = db.Column(db.String(64), unique=True, nullable=False)
    tags = db.relationship('Tag', secondary=file_tag, lazy='subquery', backref=db.backref('files', lazy=True))

    def __repr__(self):
        return '<File {}>'.format(self.filename)

class Tag(Resource):
    __tablename__ = 'tags'
    __mapper_args__ = {
        'polymorphic_identity': 'tag'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)