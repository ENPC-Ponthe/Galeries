

# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify, Blueprint
from werkzeug import secure_filename
from flask_mail import Message
import os
from flask_login import UserMixin, login_user , logout_user , current_user , login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from .. import app, db
from ..models import Year, Event, File, Category
import os

liste_char=string.ascii_letters+string.digits

# dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
#     user="enpc-ponthe",password="Ponthasm7gorique2017", \
#     database="enpc-ponthe")

DOSSIER_UPS = os.path.join(app.instance_path, 'uploads')
directory2=DOSSIER_UPS

private = Blueprint('private', __name__)

@private.before_request     # login nécessaire pour tout le blueprint
@login_required
def before_request():
    pass
    # if g.user.role != ROLE_ADMIN:     # code pour restreindr un blueprint aux admins ;)
    #     abort(401)

def extension_ok(nomfic):
    """ Renvoie True si le fichier possede une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('png', 'jpg', 'jpeg', 'gif', 'bmp')

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. '+directory)

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
def materiel() :
    if request.method == 'POST':
        msg = Message(request.form['message'],sender= 'clubpontheenpc@gmail.com', recipients= 'clubpontheenpc@gmail.com', events = liste_ev)
        mail.send(msg)
        return render_template("mail_envoye.html" , firstname=request.form['prenom'], lastname=request.form['nom'])
    return render_events_template('materiel.html')

@private.route('/depot_fichiers', methods=['GET', 'POST'])
def depot_fichiers():
    if request.method == 'POST':
        evenement=request.form['evenement']
        annee=request.form['annee']
        if request.form['Envoyer']=='Envoyer':
            if evenement: # on verifie que evenement est non vide
                if annee: # on verifie que date est non vide
                    directory=DOSSIER_UPS+annee+'/'
                    createFolder(directory)
                    directory2=directory+evenement+'/'
                    createFolder(directory2)
                    return redirect(url_for('upload', annee=annee, event=evenement))
                else:
                    flash("Veuillez indiquer la date de l'événement","error")
            else:
                flash("Veuillez indiquer le nom de l'événement","error")
        if request.form['Envoyer']=='create_event':
            return redirect('/create_event')
        if request.form['Envoyer']=='create_annee':
            return redirect('/create_annee')
    list_events = [event.name for event in Event.query.all()]
    list_years = [year.value for year in Year.query.order_by(Year.value).all()]

    return render_events_template('depot_fichiers.html', liste_events=list_events, liste_annees=list_years)


@private.route ('/archives/<category_slug>')
def archives_categorie(category_slug):
    category = Category.query.filter_by(slug=category_slug).one()
    events_from_cat = Event.query.all()
    files_from_cat = File.query.join(File.event).join(Event.category).filter_by(slug=category_slug).all()
    galleries = { (file.year, file.event) for file in files_from_cat }
    liste_events_annees = [[event, year.slug, event.cover_image.filename if event.cover_image is not None else File.query.filter_by(event=event).first().filename] for (year, event) in galleries]    # A changer
    return render_events_template('archives_categorie.html', category=category, liste_events_annees=liste_events_annees)


@private.route('/archive/<year>')
def archives_annee(year):
    queried_year = Year.query.filter_by(slug=year).one()
    events_from_year = Event.query.filter(File.query.filter_by(year=queried_year, event_id=Event.id).exists()).all()
    dict_events_annee = { event: event.cover_image.filename if event.cover_image is not None else File.query.filter_by(event=event).first().filename for event in events_from_year }
    return render_events_template('archives_annee.html', year_slug=year, events_annee=dict_events_annee)

@private.route('/archives/<year>/<event>')
def archives_evenement(year,event):
    files = File.query.join(File.year).join(File.event).filter(Year.slug == year, Event.slug == event).all() # à remplacer par les slugs
    filenames = [file.filename for file in files]
    event_name = Event.query.filter_by(slug=event).one().name
    return render_events_template('archives_evenement.html', year_slug=year, event_name=event_name, filenames=filenames)

@private.route('/create_event', methods=['GET', 'POST'])
def create_event():
    liste_annees = [year.value for year in Year.query.all()]

    if request.method == 'POST':
        new_event_name=request.form['new_event']
        if new_event_name:
            new_event = Event(name=new_event_name)
            db.session.add(new_event)
            db.session.commit()
            return redirect('/depot_fichiers')
        else:
            flash("Veuillez indiquer le nom du nouvel événement","error")
    return render_events_template('create_event.html', liste_annees=liste_annees)

@private.route('/create_annee', methods=['GET', 'POST'])
def create_annee():
    if request.method == 'POST':
        new_year_value = request.form['new_annee']
        if new_year_value:
            new_year = Event(name=new_year_value)
            db.session.add(new_year)
            db.session.commit()
            return redirect('depot_fichiers')
    else:
        flash("Veuillez indiquer la nouvelle année","error")
    return render_events_template('create_annee.html')

@private.route('/upload/<annee>/<event>', methods=['GET', 'POST'])
def upload(annee, event):
    t1=True
    t2=True
    if request.method == 'POST':
        for f in request.files.getlist('photos'):
            if f:
                if extension_ok(f.filename.lower()): # on verifie que son extension est valide
                    _, ext = os.path.splitext(f.filename)
                    filename = ""
                    for i in range(54):
                        filename += liste_char[random.randint(0,len(liste_char)-1)]
                    filename= filename + ext
                    f.save( DOSSIER_UPS + annee + '/' + event + '/' + filename)
                    event = Event.query.filter_by(name=event).one()
                    year = Year.query.filter_by(value=annee).one()
                    new_file = File(event=event, year=year, filename=filename)
                    db.session.add(new_file)
                    db.session.commit()
                else:
                    t1=False
            else:
                t2=False
        if t1==True:
            if t2==True:
                flash("Bravo! Vos images ont été envoyées! :)","success")
            else:
                flash("Vous avez oublié le fichier !", "error")
        if t1==False:
            flash("Ce fichier ne porte pas l'extension png, jpg, jpeg, gif ou bmp !", "error")
    return render_events_template('upload.html')

@private.route('/membres')
def membres():
    return render_events_template('/membres.html')
