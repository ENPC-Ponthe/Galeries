from flask import redirect, render_template, url_for
from flask_login import current_user

from . import app
from .services import GalleryService


@app.context_processor
def inject_top_menu_gallery_variables():
    if current_user.is_authenticated:
        return dict(top_menu_galleries_by_year=GalleryService.get_galleries_by_year(current_user))
    return dict()


# handle login failed
@app.errorhandler(401)
def handle_error(e: Exception):
    return redirect(url_for('public.login'))


@app.errorhandler(404)
def page_not_found(e: Exception):
    return render_template('404.html'), 404
