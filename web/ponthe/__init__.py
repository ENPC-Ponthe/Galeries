from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('ponthe.cfg')

from ponthe.public.views import public
from ponthe.users.views import users

# register the blueprints
app.register_blueprint(public)
app.register_blueprint(users)
