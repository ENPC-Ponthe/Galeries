from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .logging_config import logging_init

logging_init()

app = Flask(__name__, instance_relative_config=True)
app.logger.propagate = True
app.config.from_pyfile('ponthe.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

from .public import public
from .private import private
from .admin import admin
from .api import api

from . import models
from . import views

app.register_blueprint(public)
app.register_blueprint(private)
app.register_blueprint(admin)
app.register_blueprint(api, url_prefix='/api')