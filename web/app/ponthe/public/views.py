# -- coding: utf-8 --"

import re

from flask import render_template, request, flash, redirect, url_for, abort
from urllib.parse import urlparse, urljoin
from flask_login import login_user, current_user
from itsdangerous import SignatureExpired, BadSignature
from datetime import datetime

from . import public
from .. import app, db, login_manager
from ..private.views import get_home
from ..services import UserService
from ..config import constants
from ..persistence import UserDAO


def is_safe_url(target: str):  # empêche les redirections malicieuses
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


@login_manager.user_loader
def user_loader(id: int):
    user = UserDAO.get_by_id(id)
    if user is None:
        return
    else:
        return user


def get_login_page():
    return render_template('login.html')


@public.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return get_home()
        else:
            return get_login_page()

    email = request.form['email']
    password = request.form['password']
    logging_user = UserDAO.find_by_email(email)

    if logging_user is None:
        flash("Identifiants incorrectes", "error")
        return get_login_page()
    if not logging_user.email_confirmed:
        if (datetime.utcnow() - logging_user.created).total_seconds() > 3600:
            db.session.delete(logging_user)
            db.session.commit()
        else:
            flash("Compte en attente de confirmation par email", "error")
            return get_login_page()
    if logging_user.check_password(password):
        login_user(logging_user)
        app.logger.debug("Logging user: ", logging_user)
        next = get_redirect_target()
        return redirect(next) if next and urlparse(next).path != '/logout' else get_home()
    else:
        flash("Identifiants incorrectes", "error")
        return get_login_page()


@public.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        username = request.form['local_email']
        password = request.form['password']
        promotion = request.form['promotion']
        if password != request.form['confirmation_password']:
            flash("Les deux mots de passe ne correspondent pas.", "error")
        elif not re.fullmatch(r"[a-z0-9\-]+\.[a-z0-9\-]+", username):
            flash(
                "Votre adresse email doit être de la forme prenom.nom@eleves.enpc.fr ou prenom et nom ne peuvent "
                "contenir que des lettres minuscules, des chiffres et des tirets.",
                "error")
        else:
            try:
                new_user = UserService.register(username, firstname, lastname, password, promotion)
            except ValueError:
                flash("Il existe déjà un compte pour cet adresse email", "error")
                return render_template('register.html')
            flash("Email de confirmation envoyé à {}".format(new_user.email), "success")

    return render_template('register.html', AVAILABLE_PROMOTIONS=constants.AVAILABLE_PROMOTIONS)


@public.route('/register/<token>')
def registering(token: str):
    user_id: int
    try:
        user_id = UserService.get_id_from_token(token)
    except BadSignature:
        abort(404)
    except SignatureExpired:
        return render_template('mail_confirmation.html',
                               title="Erreur",
                               body='Le token est expiré. Tu as dépassé le délai de 24h.'
                               )

    user = UserDAO.get_by_id(user_id)
    if user is None:
        return render_template('mail_confirmation.html',
                               title="Erreur - Aucun utilisateur correspondant",
                               body='Réitère la procédure de création de compte.'
                               )
    user.email_confirmed = True
    db.session.commit()
    return render_template('mail_confirmation.html',
                           title="Compte validé",
                           body='Rend toi vite sur la <a href="{}">page de connexion</a> !'.format(
                               url_for('public.login'))
                           )


@public.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form['email']
        UserService.reset(email)
        flash("Si un compte est associé à cette adresse email, un email t'as été envoyé", "success")
    return render_template('reset.html')


@public.route('/reset/<token>', methods=['GET', 'POST'])
def resetting(token: str):
    user_id: int
    try:
        user_id = UserService.get_id_from_token(token)
        if user_id is None:
            abort(404)
    except BadSignature:
        abort(404)
    except SignatureExpired:
        return render_template('mail_confirmation.html',
                               title="Erreur",
                               body='Le token est expiré. Tu as dépassé le délai de 24h.'
                               )

    user = UserDAO.get_by_id(user_id)
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
            return redirect('login')

    return render_template('resetting.html', firstname=user.firstname)


@public.route('/cgu')
def cgu():
    return render_template('cgu.html')
