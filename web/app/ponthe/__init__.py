from flask import Flask
from flask_cli import FlaskCLI
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_thumbnails import Thumbnail

from . import config
from .logging_config import logging_init

logging_init()

app = Flask(__name__, instance_relative_config=True)
app.logger.propagate = True
config.load(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
FlaskCLI(app)
thumb = Thumbnail(app)
jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

from .core import public, private, admin, api, models
from .campaign import campaign

from . import cli, views

app.register_blueprint(public)
app.register_blueprint(private)
app.register_blueprint(admin)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(campaign, url_prefix='/api/campaign')
