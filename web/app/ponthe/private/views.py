# -- coding: utf-8 --"
from flask import render_template, request, flash, redirect
from flask_login import logout_user, current_user, login_required
from flask_mail import Message
from flask_tus_ponthe import tus_manager
import os

from . import private
from .. import app, db, mail
from ..admin.views import batch_upload
from ..file_helper import create_folder, move_file, is_image, is_video, get_extension
from ..models import Year, Event, File, Category, Gallery
from ..persistence import GalleryDAO

UPLOAD_FOLDER = os.path.join(app.instance_path, 'club_folder', 'uploads')
UPLOAD_TMP_FOLDER = os.path.join(app.instance_path, 'upload_tmp')

tm = tus_manager(private, upload_url='/file-upload', upload_folder=UPLOAD_TMP_FOLDER)


@tm.upload_file_handler
def upload_file_handler(upload_file_path, filename, gallery_slug):
    gallery = Event.query.filter_by(slug=gallery_slug).one()
    new_file = File(gallery=gallery, extension=get_extension(filename), author=current_user, pending=(not current_user.admin))

    if is_image(filename):
        new_file.type = "IMAGE"
    elif is_video(filename):
        new_file.type = "VIDEO"
    else:
        raise ValueError("File extension not supported")

    gallery_folder = os.path.join(UPLOAD_FOLDER, gallery_slug)
    create_folder(gallery_folder)
    move_file(upload_file_path, os.path.join(gallery_folder, new_file.filename))  # can't use os.rename to move to docker volume : OSError: [Errno 18] Invalid cross-device link
    db.session.add(new_file)
    db.session.commit()


@private.before_request     # login nécessaire pour tout le blueprint
@login_required
def before_request():
    pass


def render_events_template(template, **kwargs):
    galleries_by_year = { year: GalleryDAO.find_by_year(year) for year in Year.query.order_by(Year.value).all() }
    for year, galleries in list(galleries_by_year.items()):
        if not galleries:
            del galleries_by_year[year]
    return render_template(template, top_menu_galleries_by_year=galleries_by_year, **kwargs)


@private.route('/')
def getHome():
    return redirect('/index')


@private.route('/index')
def index():
    return render_events_template('index.html', categories=Category.query.all())


@private.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


@private.route('/materiel',methods=['GET','POST'])
def materiel():
    if request.method == 'POST':
        object = request.form['object']
        message = request.form.get('message')
        if not message:
            flash("Veuillez saisir un message", "error")
        else:
            msg = Message(subject=f"Demande d'emprunt de {object} par {current_user.firstname} {current_user.lastname}", body=message, sender=f"{current_user.full_name} <no-reply@ponthe.enpc.org>", recipients=['ponthe@liste.enpc.fr'])
            mail.send(msg)
            flash("Mail envoyé !", "success")
    return render_events_template('materiel.html')


@private.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form['option']=='create_event':
            return redirect('/create-event')
        if request.form['option']=='create_year':
            return redirect('/create-year')
        if request.form['option']=='create_gallery':
            return redirect('/create-gallery')
        if request.form['option']=='batch_upload':
            if current_user.admin:
                batch_upload()

    pending_files_by_gallery = {}
    confirmed_files_by_gallery = {}
    galleries = Gallery.query.all()
    for gallery in galleries:
        for file in gallery.files:
            if file.author != current_user:
                continue
            if file.pending:
                if gallery not in pending_files_by_gallery:
                    pending_files_by_gallery[gallery] = []
                pending_files_by_gallery[gallery].append(file)
            else:
                if gallery not in confirmed_files_by_gallery:
                    confirmed_files_by_gallery[gallery] = []
                confirmed_files_by_gallery[gallery].append(file)

    return render_events_template('dashboard.html', pending_files_by_gallery=pending_files_by_gallery, confirmed_files_by_gallery=confirmed_files_by_gallery)


@private.route('/upload/<gallery_slug>')
def upload(gallery_slug):
    gallery = GalleryDAO.find_by_slug(gallery_slug)
    return render_events_template('upload.html', gallery=gallery)


@private.route ('/categories/<category_slug>')
def category_gallery(category_slug):
    category = Category.query.filter_by(slug=category_slug).one()
    return render_events_template('category_gallery.html', category=category)

@private.route('/events/<event_slug>')
def event_gallery(event_slug):
    event = Event.query.filter_by(slug=event_slug).one()
    galleries_by_year = {}
    other_galleries = []
    for gallery in event.galleries:
        year = gallery.year
        if year is not None:
            if year not in galleries_by_year:
                galleries_by_year[year] = []
            galleries_by_year[year].append(gallery)
        else:
            other_galleries.append(gallery)

    return render_events_template(
        'event_gallery.html',
        event=event,
        galleries_by_year=galleries_by_year,
        other_galleries=other_galleries
    )

@private.route('/years/<year_slug>')
def year_gallery(year_slug):
    year = Year.query.filter_by(slug=year_slug).one()
    return render_events_template('year_gallery.html', year=year)

@private.route('/galleries/<gallery_slug>')
def gallery(gallery_slug):
    gallery = GalleryDAO.find_by_slug(gallery_slug)
    return render_events_template('gallery.html', gallery=gallery)

#@private.route('/galleries/<year_slug>/<event_slug>')
#def event_year_gallery(year_slug, event_slug):
#    galleries = GalleryDAO.find_by_event_and_year_slugs(event_slug, year_slug)
#    if len(galleries) == 1:
#        gallery_slug = galleries[0].slug
#        redirect(f"/galleries/{gallery_slug}")
#    event_name = Event.query.filter_by(slug=event_slug).one().name
#    return render_events_template('event_gallery.html', galleries=galleries)


@private.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        category_slug = request.form['category_slug']
        if name:
            new_event = Event(name=name, author=current_user)
            if category_slug:
                new_event.category = Category.query.filter_by(slug=category_slug).one()
            db.session.add(new_event)
            db.session.commit()
            return redirect('/create-gallery')
        else:
            flash("Veuillez indiquer le nom du nouvel événement","error")

    categories = Category.query.all()
    return render_events_template('create_event.html', categories=categories)


@private.route('/create-year', methods=['GET', 'POST'])
def create_year():
    if request.method == 'POST':
        new_year_value = request.form['value']
        if new_year_value:
            new_year = Year(value=new_year_value, author=current_user)
            db.session.add(new_year)
            db.session.commit()
            return redirect('/create-event')
        else:
            flash("Veuillez indiquer la nouvelle année", "error")
    return render_events_template('create_year.html')

@private.route('/create-gallery', methods=['GET', 'POST'])
def create_gallery():
    if request.method == 'POST':
        gallery_name = request.form['gallery_name']
        year_slug = request.form['year_slug']
        event_slug = request.form['event_slug']
        if gallery_name:
            new_gallery = Gallery(name=gallery_name, author=current_user)
            if year_slug:
                year = Year.query.filter_by(slug=year_slug).one()
                new_gallery.year = year
            if event_slug:
                event = Event.query.filter_by(slug=event_slug).one()
                new_gallery.event = event
            db.session.add(new_gallery)
            db.session.commit()
            return redirect('/galleries/'+new_gallery.slug)
        else:
            flash("Veuillez indiquer le nom de la nouvelle galerie", "error")

    years = Year.query.all()
    events = Event.query.all()
    return render_events_template('create_gallery.html', years=years, events=events)

@private.route('/members')
def members():
    return render_events_template('members.html')
