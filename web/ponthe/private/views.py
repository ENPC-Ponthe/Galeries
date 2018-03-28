

# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify, Blueprint
from werkzeug import secure_filename
from flask_mail import Message
import os
from flask_login import UserMixin, login_user , logout_user , current_user , login_required
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from .. import db

liste_char=string.ascii_letters+string.digits

# dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
#     user="enpc-ponthe",password="Ponthasm7gorique2017", \
#     database="enpc-ponthe")

dbconnexion = mysql.connector.connect(host="localhost", port="3306", \
    user="ponthe",password="", \
    database="ponthe")

DOSSIER_UPS = './static/uploads/'
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
    dict_events = {}
    cursor = dbconnexion.cursor()
    cursor.execute ( "SELECT DISTINCT annees FROM Dossier")
    liste_annees = cursor.fetchall()
    for annee in liste_annees :
        cursor.execute(" SELECT DISTINCT events FROM Dossier WHERE annees =  '%s' " % (annee[0]))
        liste_events = cursor.fetchall()
        dict_events[annee[0]] = [event[0] for event in liste_events]
    cursor.close()
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
    cursor = dbconnexion.cursor()
    liste_events = []
    cursor.execute("SELECT DISTINCT events FROM Events")
    var = cursor.fetchall()
    for event in var :
        liste_events.append(event[0])
    liste_annees = []
    cursor.execute("SELECT DISTINCT annees FROM Annees")
    var = cursor.fetchall()
    for annee in var :
        liste_annees.append(annee[0])
    cursor.close()
    liste_events.sort()
    liste_annees.sort()
    return render_events_template('depot_fichiers.html', liste_events=liste_events, liste_annees=liste_annees)


@private.route ('/archives/<cat>')
def archives_categorie(cat):
    cursor = dbconnexion.cursor()
    selection = " SELECT events, annees, filename FROM Dossier WHERE (couv = '%s' AND cat ='%s' )" % (1,cat)
    cursor.execute(selection)
    liste_events_annees = cursor.fetchall()
    cursor.close()
    return render_events_template('archives_categorie.html', liste_events_annees=liste_events_annees)


@private.route('/archive/<annee>')
def archives_annee(annee):
    dict_events_annee = {}
    cursor = dbconnexion.cursor()
    selection = " SELECT events,filename FROM Dossier WHERE (couv = '%s' AND annees = '%s' )" % (1,annee)
    cursor.execute(selection)
    events = cursor.fetchall()
    for event in events:
        dict_events_annee[event[0]] = event[1]
    return render_events_template('archives_annee.html', annee=annee, events_annee=dict_events_annee)

@private.route('/archives/<annee>/<event>')
def archives_evenement(annee,event):
    liste_filename = []
    cursor = dbconnexion.cursor()
    selection = "SELECT filename FROM Dossier WHERE (events = '%s' AND annees ='%s') " % (event,annee)
    cursor.execute(selection)
    var = cursor.fetchall()
    cursor.close()
    for filename in var :
        liste_filename.append(filename[0])
    return render_events_template('archives_evenement.html', annee=annee, event=event, filename=liste_filename)

@private.route('/create_event', methods=['GET', 'POST'])
def create_event():
    cursor = dbconnexion.cursor()
    cursor.execute ( "SELECT DISTINCT annees FROM Dossier")
    liste_annees = cursor.fetchall()

    if request.method == 'POST':
        new_event=request.form['new_event']
        if new_event:
            cursor = dbconnexion.cursor()
            add_event = "INSERT INTO Events (events) VALUES('%s')" % (new_event)
            cursor.execute(add_event)
            dbconnexion.commit()
            cursor.close()
            return redirect('/depot_fichiers')
        else:
            flash("Veuillez indiquer le nom du nouvel événement","error")
    return render_events_template('create_event.html', liste_annees=liste_annees)

@private.route('/create_annee', methods=['GET', 'POST'])
def create_annee():
    if request.method == 'POST':
        new_annee = request.form['new_annee']
        if new_annee:
            cursor = dbconnexion.cursor()
            add_annee = "INSERT INTO Annees (annees) VALUES('%s')" % (new_annee)
            cursor.execute(add_annee)
            dbconnexion.commit()
            cursor.close()
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
                    cursor = dbconnexion.cursor()
                    add_lien = "INSERT INTO Dossier (events,annees,filename) VALUES ('%s','%s','%s')" % (event,annee,filename)
                    cursor.execute(add_lien)
                    dbconnexion.commit()
                    cursor.close()
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
