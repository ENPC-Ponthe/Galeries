

# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify, Blueprint
from werkzeug import secure_filename
from flask_mail import Mail,Message
import os
from flask_login import LoginManager, UserMixin, login_user , logout_user , current_user , login_required
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

liste_char=string.ascii_letters+string.digits


dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
    user="enpc-ponthe",password="Ponthasm7gorique2017", \
    database="enpc-ponthe")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

s=URLSafeTimedSerializer(app.secret_key)

class User(UserMixin):
    pass

user = User()

def connexion(dict_events) :
    cursor = dbconnexion.cursor()
    cursor.execute ( "SELECT DISTINCT annees FROM Dossier")
    liste_annees = cursor.fetchall()
    for annee in liste_annees :
        cursor.execute(" SELECT DISTINCT events FROM Dossier WHERE annees =  '%s' " % (annee[0]))
        liste_events = cursor.fetchall()
        dict_events[annee[0]] = []
        for event in liste_events :
            dict_events[annee[0]].append(event[0])
    cursor.close()

@login_manager.user_loader
def user_loader(email):
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    cursor.close()
    for admin in liste_admin:
        empDict = {
            'id': admin[0],
            'lastname': admin[1],
            'firstname': admin[2],
            'email': admin[3],
            'password': admin[4]}
        users[str(admin[3])] = empDict
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    cursor.close()
    for admin in liste_admin:
        empDict = {
            'id': admin[0],
            'lastname': admin[1],
            'firstname': admin[2],
            'email': admin[3],
            'password': admin[4]}
        users[str(admin[3])] = empDict
    email = request.form.get('email')
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        user.is_authenticated = True
        return user
    else:
        return

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    for admin in liste_admin:
        empDict = {
            'id': admin[0],
            'lastname': admin[1],
            'firstname': admin[2],
            'email': admin[3],
            'password': admin[4]}
        users[str(admin[3])] = empDict
    cursor.close()
    if request.method == 'GET':
        return getLoginPage()
    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user.id = email
        login_user(user)
        return getHome()
    return getLoginPage()


@users_blueprint.route('/creation-compte', methods=['GET', 'POST'])
def creation():
    if request.method == 'POST' :
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.id = request.form['email']
        user.MDP = request.form['password']
        user.CMDP = request.form['confirmation_password']
        if user.MDP == user.CMDP :
            token = s.dumps(user.id)
            msg = Message('Confirm Email', sender = 'clubpontheenpc@gmail.com',recipients = [user.id] )
            link = url_for('confirm_email', token = token,  _external = True)
            msg.body = 'Votre lien est {}'.format(link)
            mail.send(msg)
            return render_template('mail_confirmation.html', m = user.id,)
        else :
            flash(u'Les deux mots de passe ne concordent pas', "error_password")
    return render_template('creation-compte.html')

@users_blueprint.route('/reset-password', methods =['GET','POST'])
def reset():
    if request.method == 'POST' :
        user.id = request.form['email']
        user.MDP = request.form['password']
        token = s.dumps(user.id)
        msg = Message('Reset Email' , sender = 'clubpontheenpc@gmail.com', recipients = [user.id] )
        link = url_for('reset_email', token = token, _external =True )
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', m = user.id)
    return render_template('reset-password.html')

@users_blueprint.route('/reset_email/<token>')
def reset_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        reset_admin = "UPDATE Admin SET password = '%s' WHERE email = '%s' " % (user.MDP, user.id)
        cursor.execute(reset_admin)
        dbconnexion.commit()
        cursor.close()
    except SignatureExpired :
        return '<h1> The token is expired </h1> '
    return getLoginPage()

@users_blueprint.route('/confirm_email/<token>')
def confirm_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        add_admin = "INSERT INTO Admin(lastname, firstname, email, password) VALUES('%s', '%s', '%s', '%s')" % (user.nom, user.prenom , user.id, user.MDP )
        cursor.execute(add_admin)
        dbconnexion.commit()
        cursor.close()
    except SignatureExpired :
        return '<h1> The token is expired </h1> '
    return getLoginPage()


@users_blueprint.route('/logout')
def logout():
    logout_user()
    return getHome()

# handle login failed
@users_blueprint.errorhandler(401)
def handleError(e):
    print("Erreur lors de l'authentification : ", e)
    return login()

# Authoriser la page de login
@users_blueprint.route('/login')
def getLoginPage():
    return render_template('login.html')

@users_blueprint.route('/materiel',methods=['GET','POST'])
@login_required
def reservation() :
    dict_events = {}
    connexion(dict_events)
    if request.method == 'POST':
        msg = Message(request.form['message'],sender= 'clubpontheenpc@gmail.com', recipients= 'clubpontheenpc@gmail.com', events = liste_ev)
        mail.send(msg)
        return render_template("mail_envoye.html" , p=request.form['prenom'], n=request.form['nom'])
    return render_template( 'materiel.html', dict_events = dict_events)
