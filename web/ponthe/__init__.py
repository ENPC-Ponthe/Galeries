from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('ponthe.cfg')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

from ponthe.public.views import public
from ponthe.private.views import private

from . import models
from . import views
# register the blueprints
app.register_blueprint(public)
app.register_blueprint(private)
