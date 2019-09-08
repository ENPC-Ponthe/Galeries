from flask import request, redirect, flash, abort, render_template, url_for
from flask_login import current_user, login_required

from ...dao import CategoryDAO
from ...services import YearService, EventService, GalleryService, FileService
from . import admin


@admin.before_request     # login en tant qu'admin nécessaire pour tout le blueprint
@login_required
def before_request():
    if not current_user.admin:
        abort(401)


@admin.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        category_slug = request.form['category_slug']
        event_description = request.form.get('description')
        if name:
            EventService.create(name, event_description, category_slug, current_user)
            return redirect(url_for('private.create_gallery'))
        else:
            flash("Veuillez indiquer le nom du nouvel événement","error")

    categories = CategoryDAO().find_all()
    return render_template('create_event.html', categories=categories)


@admin.route('/create-year', methods=['GET', 'POST'])
def create_year():
    if request.method == 'POST':
        year_value = request.form['value']
        year_description = request.form.get('description')
        if year_value:
            YearService.create(year_value, year_description, current_user)
            return redirect(url_for('admin.create_event'))
        else:
            flash("Veuillez indiquer la nouvelle année", "error")
    return render_template('create_year.html')


@admin.route('/moderation', methods=['GET', 'POST'])
def moderation():
    if request.method == 'POST':
        if "delete" in request.form:
            gallery_slug = request.form["delete"]
            GalleryService.delete(gallery_slug, current_user)
        if "approve" in request.form:
            gallery_slug = request.form["approve"]
            GalleryService.approve(gallery_slug, current_user)
        if 'delete_file' in request.form:
            file_slug = request.form['delete_file']
            FileService.delete(file_slug, current_user)
        if 'approve_file' in request.form:
            file_slug = request.form['approve_file']
            FileService.approve_by_slug(file_slug)

    pending_files_by_gallery = GalleryService.get_pending_files_by_gallery()
    return render_template('moderation.html', pending_files_by_gallery=pending_files_by_gallery)
