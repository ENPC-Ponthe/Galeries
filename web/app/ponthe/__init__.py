from flask import Flask
from flask_cas import CAS
from flask_cli import FlaskCLI
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_thumbnails import Thumbnail
from flask_cors import CORS

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

cas_v2 = CAS(app, '/api/cas')
cas = CAS(app, '/v1/cas')
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

from .v1.public import public
from .v1.private import private
from .v1.admin import admin
from .api.admin import admin_api
from .api.public import public_api
from .api.private import private_api

from . import cli
from . import models
from . import views

API_V1 = '/v1'
API_V2 = '/api'

app.register_blueprint(public, url_prefix=API_V1)
app.register_blueprint(private, url_prefix=API_V1)
app.register_blueprint(admin, url_prefix=API_V1)
app.register_blueprint(admin_api, url_prefix=API_V2)
app.register_blueprint(public_api, url_prefix=API_V2)
app.register_blueprint(private_api, url_prefix=API_V2)
