from flask import render_template, url_for
from flask_mail import Message

from .. import mail


class MailService:
    @staticmethod
    def send_registering_email(firstname, email, token):
        msg = Message('Confirme la validation de ton compte Ponthé', sender='Ponthé <no-reply@ponthe.enpc.org>',
                      recipients=[email])
        link = "https://ponthe-testing.enpc.org" + url_for('public.registering', token=token)
        msg.body = 'Clique sur le lien de confirmation suivant sous 24h pour activer ton compte : {}'.format(link)
        msg.html = render_template('email/register.html', register_link=link, firstname=firstname)
        mail.send(msg)

    @staticmethod
    def send_resetting_email(firstname, email, reset_link):
        msg = Message('Réinitialise ton mot de passe Ponthé', sender='Ponthé <no-reply@ponthe.enpc.org>',
                      recipients=[email])
        msg.body = 'Pour réinitialiser ton mot de passe, clique sur le lien suivant : {}'.format(reset_link)
        msg.html = render_template('email/reset.html', reset_link=reset_link, firstname=firstname)
        mail.send(msg)
