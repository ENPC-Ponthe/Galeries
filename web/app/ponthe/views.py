from flask import redirect
from . import app
from .private.views import render_events_template
import os
from flask import send_from_directory
from flask_login import login_required

@app.route('/uploads/<path:filename>')
@login_required
def uploads(filename):
    return send_from_directory(
        os.path.join(app.instance_path, 'club_folder', 'uploads'),
        filename
    )

# handle login failed
@app.errorhandler(401)
def handleError(e):
    app.logger.error(f"Erreur lors de l'authentification : {e}")
    return redirect('login')

@app.errorhandler(404)
def page_not_found(e):
    return render_events_template('404.html'), 404
