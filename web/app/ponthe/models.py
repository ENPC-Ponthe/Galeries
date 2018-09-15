from flask_login import UserMixin, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import codecs, translitcodec
import enum
from . import db
import re
import string, random

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')  #   Les slug DSI enlève les ' au lieu de les remplacer par un -
ALPHANUMERIC_LIST = string.ascii_letters+string.digits

def generate_random_string(size, char_list=ALPHANUMERIC_LIST):
    return "".join([char_list[random.randint(0,len(char_list)-1)] for i in range(size)])

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = codecs.encode(word, 'translit/long')
        if word:
            result.append(word)
    return str(delim.join(result))

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
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    groups = db.relationship('Group', secondary=membership, lazy='subquery', backref=db.backref('members', lazy=True))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, id=None, firstname=None, lastname=None, password=None, username=None, email=None, admin=None, email_confirmed=None):
        if id:
            self.id = id
        self.firstname = firstname
        self.lastname = lastname
        if username:
            self.username = username
            if not email:
                self.email = "{}@eleves.enpc.fr".format(username)
        if email:
            self.email = email
            if not username:
                self.username = email.split("@")[0]
        if password:
            self.set_password(password)
        if admin is not None:
            self.admin = admin
        if email_confirmed is not None:
            self.email_confirmed = email_confirmed

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_random_password():
        return generate_random_string(random.randint(8, 12))

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

    def __init__(self, id=None, name=None, slug=None, author=None, author_id=None):   # fixtures need initializing with ids, **kwargs cause default __init__ of subclasses give all arguments to super i gues
        self.name = name
        if id:
            self.id = id
        if slug:
            self.slug = slug
        else:
            self.set_slug(name)
        if author_id:
            self.author_id = author_id
        elif author:
            self.author = author
        #elif current_user is not None and current_user.is_authenticated:   # doesn't work
        #    self.author = current_user

    def set_slug(self, name):
        self.slug = slugify(name)

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

    def __init__(self, id=None, year=None, year_id=None, event=None, event_id=None, **kwargs):
        super().__init__(id=id, **kwargs)
        if year_id:
            self.year_id = year_id
        elif year:
            self.year = year
        if event_id:
            self.event_id = event_id
        elif event:
            self.event = event

class Reaction(TimestampMixin, db.Model):   # relation many-to-many type Slack
    __tablename__ = 'reactions'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_reactions_user'), primary_key=True)
    user = db.relationship('User', backref='reactions', foreign_keys=[user_id])
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', name='fk_reactions_resource'), primary_key=True)
    resource = db.relationship('Resource', backref='reactions', foreign_keys=[resource_id])
    type = db.Column(db.Enum(ReactionEnum), nullable=False)

    def __init__(self, id=None, user=None, user_id=None, resource=None, resource_id=None, type=None, **kwargs):
        super().__init__(id=id, **kwargs)
        if user_id:
            self.user_id = user_id
        elif user:
            self.user = user
        if resource_id:
            self.resource_id = resource_id
        elif resource:
            self.resource = resource
        self.type = type

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

    def __init__(self, id=None, text=None,resource=None, resource_id=None, **kwargs):
        super().__init__(id=id, **kwargs)
        self.text = text
        if resource_id:
            self.resource_id = resource_id
        elif resource:
            self.resource = resource

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

    def __init__(self, id=None, description=None, cover_image=None, cover_image_id=None, **kwargs):
        super().__init__(id=id, **kwargs)
        self.description = description
        if cover_image_id:
            self.cover_image_id = cover_image_id
        elif cover_image:
            self.cover_image = cover_image

    def __repr__(self):
        return '<Category {}>'.format(self.name)

class Event(Resource):
    __tablename__ = 'events'
    __mapper_args__ = {
        'polymorphic_identity': 'event'
    }
    # exemple de nom de l'event : Campagne BDE qui peut être sur plusieurs années

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', name='fk_events_category'), nullable=True)
    category = db.relationship('Category', backref='events', foreign_keys=[category_id])
    # dépendance circulaire entre table à migrer séparemment
    cover_image_id = db.Column(db.Integer, db.ForeignKey('files.id', name='fk_events_file'), nullable=True)
    cover_image = db.relationship('File', backref='events', foreign_keys=[cover_image_id])
    private = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.String(1024), nullable=True)

    def __init__(self, id=None, category=None, category_id=None, cover_image=None, cover_image_id=None, private=None, description=None, **kwargs):
        super().__init__(id=id, **kwargs)
        if category_id:
            self.category_id = category_id
        elif category:
            self.category = category
        if cover_image_id:
            self.cover_image_id = cover_image_id
        elif cover_image:
            self.cover_image = cover_image
        if private is not None:
            self.private = private
        if description:
            self.description = description

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

    def __init__(self, value=None, id=None, cover_image=None, cover_image_id=None, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = str(value)
        super().__init__(id=id, **kwargs)
        self.value = value
        if cover_image_id:
            self.cover_image_id = cover_image_id
        elif cover_image:
            self.cover_image = cover_image

    def __repr__(self):
        return '<Year {}>'.format(self.value)

file_tag = db.Table('file_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', name='fk_file_tags_tag'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id', name='fk_file_tags_file'), primary_key=True)
)

class File(Resource):   # the default slug is a 20-letter-string, just specify filename or extension
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
    pending = db.Column(db.Boolean, nullable=False, default=True)
    tags = db.relationship('Tag', secondary=file_tag, lazy='subquery', backref=db.backref('files', lazy=True))

    def __init__(self, id=None, type=None, year=None, year_id=None, event=None, event_id=None, filename=None, extension=None, pending=None, tags=None, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = generate_random_string(20)
        super().__init__(id=id, **kwargs)
        self.type = type
        if filename:
            self.filename = filename
        elif extension:
            self.filename = "{}.{}".format(self.slug, extension)
        if year_id:
            self.year_id = year_id
        elif year:
            self.year = year
        if event_id:
            self.event_id = event_id
        elif event:
            self.event = event
        if tags:
            self.tags = tags
        if pending is not None:
            self.pending = pending

    def __repr__(self):
        return '<File {}>'.format(self.filename)

class Tag(Resource):
    __tablename__ = 'tags'
    __mapper_args__ = {
        'polymorphic_identity': 'tag'
    }

    id = db.Column(db.Integer, db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
