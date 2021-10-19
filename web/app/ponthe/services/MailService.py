from flask import render_template
from flask_mail import Message
from datetime import datetime

from .. import mail

CONFIRM_EMAIL_URL = "confirm-email"
SET_NEW_PASSWORD_URL = "set-new-password"
SITE_ROOT = "https://ponthe.enpc.org"

TEAM_PHOTO_URL = "https://ponthe.enpc.org/assets/images/ponthe_teams/023_gala.jpg"


class MailService:
    @staticmethod
    def get_current_year():
        return datetime.now().year

    @staticmethod
    def render_email_template(args):
        return render_template(*args, team_photo_url=TEAM_PHOTO_URL, year=datetime.now().year)

    @staticmethod
    def send_registering_email(firstname: str, email: str, token: str):
        msg = Message('Confirme la validation de ton compte Ponthé', sender='Ponthé <no-reply@ponthe.enpc.org>',
                      recipients=[email])
        link = f'{SITE_ROOT}/{CONFIRM_EMAIL_URL}?token={token}'
        msg.body = f'Clique sur le lien de confirmation suivant sous 24h pour activer ton compte : {link}'
        msg.html = MailService.render_email_template(
            'email/register_v2.html', register_link=link, firstname=firstname)
        mail.send(msg)

    @staticmethod
    def send_resetting_email(firstname: str, email: str, reset_token: str):
        msg = Message('Réinitialise ton mot de passe Ponthé', sender='Ponthé <no-reply@ponthe.enpc.org>',
                      recipients=[email])
        reset_link = f'{SITE_ROOT}/{SET_NEW_PASSWORD_URL}?token={reset_token}'
        msg.body = f'Pour réinitialiser ton mot de passe, clique sur le lien suivant : {reset_link}'
        msg.html = MailService.render_email_template(
            'email/reset_v2.html', reset_link=reset_link, firstname=firstname)
        mail.send(msg)
