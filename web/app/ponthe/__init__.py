from flask import Flask
from flask_cli import FlaskCLI
from flask_login import LoginManager
from flask_mail import Mail
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
migrate = Migrate(app, db)
FlaskCLI(app)
thumb = Thumbnail(app)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

from .public import public
from .private import private
from .admin import admin
from .api import api_blueprint

from . import cli
from . import models
from . import views

app.register_blueprint(public)
app.register_blueprint(private)
app.register_blueprint(admin)
app.register_blueprint(api_blueprint, url_prefix='/api')
