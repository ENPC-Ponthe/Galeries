# -- coding: utf-8 --"

from . import public
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from urllib.parse import urlparse, urljoin
from flask_mail import Message
import os
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import string
import random
from .. import app, db, login_manager, mail
from ..models import User
from datetime import datetime
from sqlalchemy.exc import IntegrityError

serializer=URLSafeTimedSerializer(app.secret_key)

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

    if logging_user is None:
        flash("Identifiants incorrectes", "error")
        return getLoginPage()
    if not logging_user.email_confirmed:
        if (datetime.utcnow()-logging_user.created).total_seconds() > 3600:
            db.session.delete(logging_user)
            db.session.commit()
        else:
            flash("Compte en attente de confirmation par email", "error")
            return getLoginPage()
    if logging_user.check_password(password):
        login_user(logging_user)
        print("Logging user :", logging_user)
        next = get_redirect_target()
        return redirect(next) if next and urlparse(next).path!='/logout' else getHome()
    else:
        flash("Identifiants incorrectes", "error")
        return getLoginPage()


@public.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirmation_password']:
            flash("Les deux mots de passe ne correspondent pas", "error")
        else:
            new_user=User(
                lastname=request.form['lastname'],
                firstname=request.form['firstname'],
                username=request.form['local_email'],
                password=request.form['password'],
                admin=False,
                email_confirmed=False
            )
            db.session.add(new_user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                existing_user = User.query.filter_by(username=new_user.username).first()

                if (datetime.utcnow()-existing_user.created).total_seconds() > 3600:
                    db.session.delete(existing_user)
                    db.session.commit()
                    db.session.add(new_user)
                    db.session.commit()
                else:
                    flash("Il existe déjà un compte pour cet adresse email", "error")
                    return render_template('creation_compte.html')
            token = serializer.dumps(new_user.id)
            msg = Message('Confirme la validation de ton compte Ponthé', sender='Ponthé <no-reply@ponthe.enpc.org>', recipients=[new_user.email] )
            link = "https://ponthe.enpc.org"+url_for('public.registering', token=token)
            print(link)
            msg.body = render_template('email/register.html', register_link=link)
            mail.send(msg)

            flash("Email de confirmation envoyé à {}".format(new_user.email), "success")

    return render_template('register.html')

@public.route('/register/<token>')
def registering(token):
    try :
        user_id = serializer.loads(token, max_age=3600)
    except BadSignature:
        abort(404)
    except SignatureExpired :
        return render_template('mail_confirmation.html',
            title="Erreur",
            body='Le token est expiré. Tu as dépassé le délai de 24h.'
        )

    user = User.query.get(user_id)
    if user is None:
        return render_template('mail_confirmation.html',
            title="Erreur - Aucun utilisateur correspondant",
            body='Réitère la procédure de création de compte.'
        )
    user.email_confirmed = True
    db.session.commit()
    return render_template('mail_confirmation.html',
        title="Compte validé",
        body='Rend toi vite sur la <a href="{}">page de connexion</a> !'.format(url_for('public.login'))
    )

@public.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == 'POST' :
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.email_confirmed:
            token = serializer.dumps(user.id)
            msg = Message('Réinitialise ton mot de passe Ponthé' , sender='Ponthé <no-reply@ponthe.enpc.org>', recipients=[email])
            link = "https://ponthe.enpc.org"+url_for('public.resetting', token=token)
            # put token to user entity to retrive it in confirm_email route
            msg.body = render_template('email/reset.html', reset_link=link)
            mail.send(msg)
        flash("Si un compte est associé à cette adresse email, un email t'as été envoyé", "success")
    return render_template('reset.html')

@public.route('/reset/<token>', methods=['GET','POST'])
def resetting(token):
    try :
        user_id = serializer.loads(token, max_age=3600)
    except BadSignature:
        abort(404)
    except SignatureExpired :
        return render_template('mail_confirmation.html',
            title="Erreur",
            body='Le token est expiré. Tu as dépassé le délai de 24h.'
        )

    user = User.query.get(user_id)
    if user is None:
        return render_template('mail_confirmation.html',
            title="Erreur - Aucun utilisateur correspondant",
            body="Le compte associé n'existe plus."
        )

    if request.method == 'POST':
        new_password = request.form['new_password']
        if new_password != request.form['confirmation_password']:
            flash("Les deux mots de passe ne correspondent pas", "error")
        else:
            user.set_password(new_password)
            db.session.add(user)
            db.session.commit()
            flash("Mot de passe réinitialisé avec succès", "success")

    return render_template('resetting.html', firstname=user.firstname)
