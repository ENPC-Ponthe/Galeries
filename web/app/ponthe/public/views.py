# -- coding: utf-8 --"

from flask import render_template, request, flash, redirect, abort
from itsdangerous import SignatureExpired, BadSignature

from . import public
from .. import db
from ..services import UserService
from ..persistence import UserDAO


@public.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == 'POST' :
        email = request.form['email']
        UserService.reset(email)
        flash("Si un compte est associé à cette adresse email, un email t'as été envoyé", "success")
    return render_template('reset.html')

@public.route('/reset/<token>', methods=['GET','POST'])
def resetting(token):
    try :
        user_id = UserService.get_id_from_token(token)
        if user_id is None:
            abort(404)
    except BadSignature:
        abort(404)
    except SignatureExpired :
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
