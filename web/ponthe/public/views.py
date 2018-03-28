

# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify, Blueprint
from werkzeug import secure_filename
from urllib.parse import urlparse, urljoin
from flask_mail import Mail,Message
import os
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from .. import app, db, login_manager
from ..models import User

dbconnexion = mysql.connector.connect(host="localhost", port="3306", \
    user="ponthe",password="", \
    database="ponthe")

serializer=URLSafeTimedSerializer(app.secret_key)

public = Blueprint('public', __name__)

user= User()

def getHome():
    return redirect('index')

def is_safe_url(target):    #    empêche les redirections malicieuses
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

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
def request_loader(request):    #   sert à quoi ???
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

def getLoginPage():
    return render_template('login.html')

@public.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return getHome()
        else:
            return getLoginPage()

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

    email = request.form['email']
    password = request.form['password']
    for admin in liste_admin:
        if email == admin[3] and password == admin[4]:
            user.id = email
            login_user(user)
            next = get_redirect_target()
            return redirect(next) if next and urlparse(next).path!='/logout' else getHome()

    flash("Identifiants incorrectes", "error")
    return getLoginPage()


@public.route('/creation_compte', methods=['GET', 'POST'])
def creation_compte():
    if request.method == 'POST':
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.id = request.form['email']
        user.MDP = request.form['password']
        user.CMDP = request.form['confirmation_password']
        if user.MDP == user.CMDP :
            token = s.dumps(user.id)
            msg = Message('Confirm Email', sender = 'clubpontheenpc@gmail.com', recipients = [user.id] )
            link = url_for('confirm_email', token = token, _external = True)
            msg.body = 'Votre lien est {}'.format(link)
            mail.send(msg)
            return render_template('mail_confirmation.html', email = user.id,)
        else:
            flash("Les deux mots de passe ne concordent pas", "error")
    return render_template('creation_compte.html')

@public.route('/reset_password', methods =['GET','POST'])
def reset_password():
    if request.method == 'POST' :
        user.id = request.form['email']
        user.MDP = request.form['password']
        token = s.dumps(user.id)
        msg = Message('Reset Email' , sender = 'clubpontheenpc@gmail.com', recipients = [user.id] )
        link = url_for('reset_email', token = token, _external =True )
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', email = user.id)
    return render_template('reset_password.html')

@public.route('/reset_email/<token>')
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

@public.route('/confirm_email/<token>')
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
