# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify, Blueprint
from werkzeug import secure_filename
from urllib.parse import urlparse, urljoin
from flask_mail import Mail, Message
import os
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string
import random
from .. import app, db, login_manager
from ..models import User

serializer=URLSafeTimedSerializer(app.secret_key)

public = Blueprint('public', __name__)

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
def user_loader(id):
    user = User.query.get(id)
    if user is None:
        return
    else:
        return user


#@login_manager.request_loader
#def request_loader(request):    #   sert à quoi ???
#    email = request.form['email']
#    password = request.form['password']
#    logging_user = User.query.filter_by(email=email, password=password).first()
#
#    if logging_user is not None:
#        logging_user.is_authenticated = True
#        return logging_user
#    else:
#        return

def getLoginPage():
    return render_template('login.html')

@public.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return getHome()
        else:
            return getLoginPage()

    email = request.form['email']
    password = request.form['password']
    logging_user = User.query.filter_by(email=email).first()

    if logging_user is not None and logging_user.check_password(password):
        login_user(logging_user)
        print(logging_user)
        next = get_redirect_target()
        return redirect(next) if next and urlparse(next).path!='/logout' else getHome()
    else:
        flash("Identifiants incorrectes", "error")
        return getLoginPage()


@public.route('/creation_compte', methods=['GET', 'POST'])
def creation_compte():
    if request.method == 'POST':
        user= User(
            lastname = request.form['nom']
            firstname = request.form['prenom']
            email = request.form['email']
            password = request.form['password']
        )
        confirmation_password = request.form['confirmation_password']
        if user.password == confirmation_password :
            token = serializer.dumps(user.email)
            msg = Message('Confirm Email', sender='clubpontheenpc@gmail.com', recipients=[user.email] )
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Votre lien est {}'.format(link)
            mail.send(msg)
            return render_template('mail_confirmation.html', email=user.email)
        else:
            flash("Les deux mots de passe ne concordent pas", "error")
    return render_template('creation_compte.html')

@public.route('/reset_password', methods =['GET','POST'])
def reset_password():
    if request.method == 'POST' :
        user.email = request.form['email']
        user.password = request.form['password']
        token = serializer.dumps(user.email)
        msg = Message('Reset Email' , sender='clubpontheenpc@gmail.com', recipients=[user.email])
        link = url_for('reset_email', token=token, _external=True)
        # put token to user entity to retrive it in confirm_email route
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', email=user.email)
    return render_template('reset_password.html')

@public.route('/reset_email/<token>')   # Never finished
def reset_email(token):
    try :
        email = serializer.loads(token, max_age=300)    # what !?
        reset_user = User.query.filter_by(email=email)
        reset_user.password = user.password
        db.session.commit()

    except SignatureExpired :
        return '<h1> The token is expired </h1> '
    return getLoginPage()

@public.route('/confirm_email/<token>')  # Never finished
def confirm_email(token):
    # user not defined : it must be retrieved from database by token : add token field to model
    try :
        email = serializer.loads(token, max_age=300)    # what !?
        new_user = User(id=user.id, firstname=user.firstname, lastname=user.lastname, password=user.password)
        db.session.add(new_user)
        db.session.commit()
    except SignatureExpired :
        return '<h1> The token is expired </h1> '
    return getLoginPage()
