# -- coding: utf-8 --"
import os

from flask import render_template, request, flash, redirect, url_for, send_file
from flask_login import logout_user, current_user, login_required
from flask_mail import Message
from flask_tus_ponthe import tus_manager
from sqlalchemy.orm.exc import NoResultFound

from werkzeug.exceptions import NotFound

from . import private
from ... import app, mail
from ...dao import EventDAO, YearDAO, CategoryDAO, GalleryDAO
from ...services import FileService, GalleryService

UPLOAD_FOLDER = app.config['MEDIA_ROOT']
UPLOAD_TMP_FOLDER = app.config['UPLOAD_TMP_ROOT']
print(UPLOAD_TMP_FOLDER)
tm = tus_manager(private, upload_url='/v1/file-upload', upload_folder=UPLOAD_TMP_FOLDER)


@tm.upload_file_handler
def upload_file_handler(upload_file_path, filename, gallery_slug):
    FileService.create(upload_file_path, filename, gallery_slug, current_user)


@private.before_request     # login nécessaire pour tout le blueprint
@login_required
def before_request():
    pass


@private.route('/')
def get_home():
    return redirect(url_for('private.index'))

@private.route('/uploads/<path:file_path>')
def uploads(file_path: str):
    try:
        return send_file(os.path.join(app.config['MEDIA_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()


@private.route('/thumbs/<path:file_path>')  # utilisé en dev, en prod c'était servi par le serveur web
def thumbnails(file_path: str):
    try:
        return send_file(os.path.join(app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'], file_path))
    except FileNotFoundError:
        raise NotFound()


@private.route('/index')
def index():
    return render_template('index.html', categories=CategoryDAO().find_all())


@private.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.login'))


@private.route('/materiel',methods=['GET','POST'])
def materiel():
    if request.method == 'POST':
        object = request.form['object']
        message = request.form.get('message')
        if not message:
            flash("Veuillez saisir un message", "error")
        else:
            msg = Message(subject=f"Demande d'emprunt de {object} par {current_user.firstname} {current_user.lastname}",
                          body=message,
                          sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>",
                          recipients=['ponthe@liste.enpc.fr'])
            mail.send(msg)
            flash("Mail envoyé !", "success")
    return render_template('materiel.html')


@private.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get('option') == 'create_event':
            return redirect(url_for('admin.create_event'))
        if request.form.get('option') == 'create_year':
            return redirect(url_for('admin.create_year'))
        if request.form.get('option') == 'create_gallery':
            return redirect(url_for('private.create_gallery'))
        if request.form.get('option') == 'moderate':
            return redirect(url_for('admin.moderation'))
        if 'delete_file' in request.form:
            file_slug = request.form['delete_file']
            FileService.delete(file_slug, current_user)
        if 'make_gallery_public' in request.form:
            gallery_slug = request.form['make_gallery_public']
            GalleryService.make_public(gallery_slug, current_user)
        if 'make_gallery_private' in request.form:
            gallery_slug = request.form['make_gallery_private']
            GalleryService.make_private(gallery_slug, current_user)

    pending_files_by_gallery, confirmed_files_by_gallery = GalleryService.get_own_pending_and_approved_files_by_gallery(current_user)

    return render_template('dashboard.html', pending_files_by_gallery=pending_files_by_gallery, confirmed_files_by_gallery=confirmed_files_by_gallery)


@private.route('/upload/<gallery_slug>')
def upload(gallery_slug):
    gallery = GalleryDAO().find_by_slug(gallery_slug)
    return render_template('upload.html', gallery=gallery)


@private.route ('/categories/<category_slug>')
def category_gallery(category_slug):
    try:
        category = CategoryDAO().find_by_slug(category_slug)
    except NoResultFound:
        raise NotFound()
    return render_template('category_gallery.html', category=category)

@private.route('/events/<event_slug>', methods=['GET', 'POST'])
def event_gallery(event_slug):
    event_dao = EventDAO()
    if request.method == 'POST' and "delete" in request.form and current_user.admin:
        event_dao.delete_detaching_galleries(event_slug)
        return redirect(url_for("private.index"))
    try:
        event = event_dao.find_by_slug(event_slug)
    except NoResultFound:
        raise NotFound()
    galleries_by_year = {}
    other_galleries = []
    for gallery in event.galleries:
        if gallery.private:
            continue
        year = gallery.year
        if year is not None:
            if year not in galleries_by_year:
                galleries_by_year[year] = []
            galleries_by_year[year].append(gallery)
        else:
            other_galleries.append(gallery)

    return render_template(
        'event_gallery.html',
        event=event,
        galleries_by_year=galleries_by_year,
        other_galleries=other_galleries
    )

@private.route('/years/<year_slug>', methods=['GET', 'POST'])
def year_gallery(year_slug):
    year_dao = YearDAO()
    if request.method == 'POST' and "delete" in request.form and current_user.admin:
        year_dao.delete_detaching_galleries(year_slug)
        return redirect(url_for("private.index"))
    try:
        year = year_dao.find_by_slug(year_slug)
    except NoResultFound:
        raise NotFound()
    public_galleries = list(filter(lambda gallery: not gallery.private, year.galleries))
    return render_template('year_gallery.html', year=year, public_galleries=public_galleries)

@private.route('/galleries/<gallery_slug>', methods=['GET', 'POST'])
def gallery(gallery_slug):
    if request.method == 'POST':
        if "delete" in request.form and current_user.admin:
            GalleryService.delete(gallery_slug, current_user)
            return redirect(url_for("private.index"))
        if 'delete_file' in request.form:
            file_slug = request.form['delete_file']
            FileService.delete(file_slug, current_user)
        if 'make_gallery_public' in request.form:
            GalleryService.make_public(gallery_slug, current_user)
        if 'make_gallery_private' in request.form:
            GalleryService.make_private(gallery_slug, current_user)
        if 'approve_file' in request.form and current_user.admin:
            file_slug = request.form['approve_file']
            FileService.approve_by_slug(file_slug)
    try:
        gallery = GalleryDAO().find_by_slug(gallery_slug)
    except NoResultFound:
        raise NotFound()
    if gallery.private and not GalleryDAO.has_right_on(gallery, current_user):
        raise NotFound()
    return render_template('gallery.html', gallery=gallery, approved_files=filter(lambda file: not file.pending, gallery.files))


@private.route('/create-gallery', methods=['GET', 'POST'])
def create_gallery():
    if request.method == 'POST':
        gallery_name = request.form['name']
        gallery_description = request.form.get('description')
        year_slug = request.form.get('year_slug')
        event_slug = request.form.get('event_slug')
        private = request.form.get('private')
        if gallery_name:
            gallery = GalleryService.create(gallery_name, current_user, gallery_description, private == "on", year_slug, event_slug)
            return redirect(url_for("private.gallery", gallery_slug=gallery.slug))
        else:
            flash("Veuillez indiquer le nom de la nouvelle galerie", "error")

    years = YearDAO().find_all()
    events = EventDAO().find_all()
    return render_template('create_gallery.html', years=years, events=events)

@private.route('/members')
def members():
    return render_template('members.html')
