from flask import redirect, send_from_directory, send_file
from flask_login import login_required
import os

from werkzeug.exceptions import NotFound

from . import app
from .private.views import render_events_template

@app.route('/uploads/<path:file_path>')
@login_required
def uploads(file_path):
    try:
        return send_file(os.path.join(app.config['MEDIA_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()

@app.route('/thumbs/<path:file_path>')
@login_required
def thumbnails(file_path):
    try:
        return send_file(os.path.join(app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()

@app.route('/apk/<path:filename>')
def apk(filename):
    try:
        return send_from_directory(
            os.path.join(app.instance_path, 'club_folder', 'apk'),
            filename
        )
    except FileNotFoundError:
        raise NotFound()

# handle login failed
@app.errorhandler(401)
def handleError(e):
    return redirect('login')

@app.errorhandler(404)
def page_not_found(e):
    return render_events_template('404.html'), 404
