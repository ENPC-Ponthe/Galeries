from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('ponthe.cfg')

from ponthe.users.views import users_blueprint
from ponthe.files.views import files_blueprint

# register the blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(files_blueprint)
