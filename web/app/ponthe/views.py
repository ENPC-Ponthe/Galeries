from flask import redirect, send_file, render_template
from flask_login import login_required, current_user
import os

from werkzeug.exceptions import NotFound

from . import app
from .services import GalleryService


@app.context_processor
def inject_top_menu_gallery_variables():
    if current_user.is_authenticated:
        return dict(top_menu_galleries_by_year=GalleryService.get_galleries_by_year())
    return dict()


@app.route('/uploads/<path:file_path>')
@login_required
def uploads(file_path: str):
    try:
        return send_file(os.path.join(app.config['MEDIA_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()


@app.route('/thumbs/<path:file_path>')  # utilisé en dev, en prod c'est servi par le serveur web
@login_required
def thumbnails(file_path: str):
    try:
        return send_file(os.path.join(app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()


@app.route('/assets/<path:file_path>')  # utilisé en dev, en prod c'est servi par le serveur web
def assets(file_path: str):
    try:
        return send_file(os.path.join(app.config['ASSET_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()


# handle login failed
@app.errorhandler(401)
def handle_error(e: Exception):
    return redirect('login')


@app.errorhandler(404)
def page_not_found(e: Exception):
    return render_template('404.html'), 404
