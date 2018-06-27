# -- coding: utf-8 --"

from . import private
from flask import Flask,render_template,request, flash, redirect, url_for, jsonify
from werkzeug import secure_filename
from flask_mail import Message
import os
from flask_login import UserMixin, login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from .. import app, db, mail
from ..models import Year, Event, File, Category
from ..file_helper import create_folder, move_file, is_image, is_video, ext
import os, subprocess
from flask_tus_ponthe import tus_manager
from ..admin.views import batch_upload

# dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
#     user="enpc-ponthe",password="Ponthasm7gorique2017", \
#     database="enpc-ponthe")

UPLOAD_FOLDER = os.path.join(app.instance_path, 'club_folder', 'uploads')
UPLOAD_TMP_FOLDER = os.path.join(app.instance_path, 'upload_tmp')

tm = tus_manager(private, upload_url='/file-upload', upload_folder=UPLOAD_TMP_FOLDER)

def get_filenames(year_slug, event_slug):
    files = File.query.join(File.year).join(File.event).filter(Year.slug == year_slug, Event.slug == event_slug).all() # à remplacer par les slugs
    return [file.filename for file in files]

def get_moderation_filenames(year_slug, event_slug):    # retourne la liste des fichiers non-modérés et la liste des fichiers modérés
    files = File.query.join(File.year).join(File.event).filter(Year.slug == year_slug, Event.slug == event_slug).all() # à remplacer par les slugs
    return [file.filename for file in files if file.pending], [file.filename for file in files if not file.pending]

@tm.upload_file_handler
def upload_file_hander(upload_file_path, filename, year_value, event_name):
    event = Event.query.filter_by(name=event_name).one()
    year = Year.query.filter_by(value=year_value).one()
    new_file = File(event=event, year=year, extension=ext(filename), author=current_user, pending=True)

    if is_image(filename):
        new_file.type = "IMAGE"
    elif is_video(filename):
        new_file.type = "VIDEO"
    else:
        raise ValueError("File extension not supported")

    gallery_folder = os.path.join(UPLOAD_FOLDER, str(year_value), str(event_name))
    create_folder(gallery_folder)
    move_file(upload_file_path, os.path.join(gallery_folder, new_file.filename))  # can't use os.rename to move to docker volume : OSError: [Errno 18] Invalid cross-device link
    db.session.add(new_file)
    db.session.commit()

@private.before_request     # login nécessaire pour tout le blueprint
@login_required
def before_request():
    pass

def render_events_template(template, **kwargs):
    dict_events = { year: Event.query.filter(File.query.filter_by(year=year, event_id=Event.id).exists()).all() for year in Year.query.order_by(Year.value).all() }
    return render_template(template, dict_events=dict_events, **kwargs)

@private.route('/')
def getHome():
    return redirect('/index')

@private.route('/index')
def index():
    return render_events_template('index.html')

@private.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@private.route('/materiel',methods=['GET','POST'])
def materiel() :    # TODO
    if request.method == 'POST':
        msg = Message(subject="Demande d'emprunt de {} par {} {}".format(request.form['object'], current_user.firstname, current_user.lastname), body=request.form['message'], sender='Ponthé <no-reply@ponthe.enpc.org>', recipients=['philippe.ferreira-de-sousa@eleves.enpc.fr'])
        mail.send(msg)
    return render_events_template('materiel.html')

@private.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form['option']=='create_event':
            return redirect('/create_event')
        if request.form['option']=='create_year':
            return redirect('/create_year')
        if request.form['option']=='batch_upload':
            if current_user.admin:
                batch_upload()
    list_events = [event for event in Event.query.filter_by(author=current_user).all()]
    list_years_slug = [year.slug for year in Year.query.order_by(Year.value).all()]
    pending_galleries = []
    confirmed_galleries = []
    for year_slug in list_years_slug:
        for event in list_events:
            pending_filenames, confirmed_filenames = get_moderation_filenames(year_slug, event.slug)
            if pending_filenames:
                pending_galleries.append((year_slug, event.name, pending_filenames))
            if confirmed_filenames:
                confirmed_galleries.append((year_slug, event.name, confirmed_filenames))
    return render_events_template('dashboard.html', pending_galleries=pending_galleries, confirmed_galleries=confirmed_galleries)

@private.route('/upload/<year>/<event>')
def upload(year, event):
    return render_events_template('upload.html', year=year, event=event)

@private.route ('/category/<category_slug>')
def category_gallery(category_slug):
    category = Category.query.filter_by(slug=category_slug).one()
    events_from_cat = Event.query.all()
    files_from_cat = File.query.join(File.event).join(Event.category).filter_by(slug=category_slug).all()
    galleries = { (file.year, file.event) for file in files_from_cat }
    liste_events_annees = [[event, year.slug, event.cover_image.filename if event.cover_image is not None else File.query.filter_by(event=event).first().filename] for (year, event) in galleries]    # A changer
    return render_events_template('category_gallery.html', category=category, liste_events_annees=liste_events_annees)


@private.route('/galleries/<year_slug>')
def year_gallery(year_slug):
    queried_year = Year.query.filter_by(slug=year_slug).one()
    events_from_year = Event.query.filter(File.query.filter_by(year=queried_year, event_id=Event.id).exists()).all()
    dict_events_annee = { event: event.cover_image.filename if event.cover_image is not None else File.query.filter_by(event=event).first().filename for event in events_from_year }
    return render_events_template('year_gallery.html', year_slug=year_slug, events_annee=dict_events_annee)

@private.route('/galleries/<year_slug>/<event_slug>')
def event_gallery(year_slug, event_slug):
    filenames = get_filenames(year_slug, event_slug)
    event_name = Event.query.filter_by(slug=event_slug).one().name
    return render_events_template('event_gallery.html', year_slug=year_slug, event_name=event_name, filenames=filenames)

@private.route('/create-event', methods=['GET', 'POST'])
def create_event():
    liste_annees = [year.value for year in Year.query.all()]

    if request.method == 'POST':
        new_event_name=request.form['new_event']
        if new_event_name:
            new_event = Event(name=new_event_name)
            db.session.add(new_event)
            db.session.commit()
            return redirect('/dashboard')
        else:
            flash("Veuillez indiquer le nom du nouvel événement","error")
    return render_events_template('create_event.html', liste_annees=liste_annees)

@private.route('/create-year', methods=['GET', 'POST'])
def create_annee():
    if request.method == 'POST':
        new_year_value = request.form['new_annee']
        if new_year_value:
            new_year = Event(name=new_year_value)
            db.session.add(new_year)
            db.session.commit()
            return redirect('/dashboard')
    else:
        flash("Veuillez indiquer la nouvelle année","error")
    return render_events_template('create_annee.html')

@private.route('/membres')
def membres():
    return render_events_template('membres.html')
