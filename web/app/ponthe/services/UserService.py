import csv

from datetime import datetime
from typing import TextIO
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
from flask import render_template
from flask_mail import Message
from smtplib import SMTPException


from .. import app, db, mail
from ..models import User
from ..dao import UserDAO
from .MailService import MailService


serializer=URLSafeTimedSerializer(app.secret_key)


class UserService:
    @staticmethod
    def get_token(user: User):
        return serializer.dumps(user.id)

    @staticmethod
    def get_id_from_token(token: str):
        return serializer.loads(token, max_age=3600)

    @classmethod
    def get_reset_link(cls, user: User):
        return f"ponthe.enpc.org/reset/{cls.get_token(user)}"

    @classmethod
    def register(cls, username: str, firstname: str, lastname: str, password: str, promotion: str):
        new_user = User(
            lastname=lastname,
            firstname=firstname,
            username=username,
            password=password,
            promotion=promotion,
            admin=False,
            email_confirmed=False
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            existing_user = UserDAO.find_by_username(new_user.username)

            if not existing_user.email_confirmed and (datetime.utcnow() - existing_user.created).total_seconds() > 3600:
                db.session.delete(existing_user)
                db.session.commit()
                db.session.add(new_user)
                db.session.commit()
            else:
                raise ValueError

        token = cls.get_token(new_user)
        MailService.send_registering_email(new_user.firstname, new_user.email, token)

        return new_user

    @classmethod
    def reset(cls, email: str):
        user = UserDAO.find_by_email(email)
        if user is not None and user.email_confirmed:
            reset_link = cls.get_reset_link(user)
            MailService.send_resetting_email(user.firstname, user.email, reset_link)

    @staticmethod
    def create_users(csv_file: TextIO):
        csv_reader = csv.reader(csv_file)
        for gender, lastname, firstname, email, origin, department, promotion in csv_reader:
            user = User(firstname=firstname, lastname=lastname, gender=gender, origin=origin, department=department,
                        promotion=promotion, email=email, admin=False, email_confirmed=True)
            password = User.generate_random_password()
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
                msg = Message('Bienvenue aux Ponts', sender='Ponthé <no-reply@ponthe.enpc.org>',
                              recipients=[user.email])
                msg.body = 'Ton club d\'audiovisuel te souhaite la bienvenue aux Ponts ! ' \
                           + 'Ton compte Ponthé a été créé sur https://ponthe.enpc.org. ' \
                           + 'Connecte-toi dès maintenant avec les identifiants suivants :\n' \
                           + 'Email : {}\n'.format(user.email) \
                           + 'Mot de passe : {}'.format(password)
                msg.html = render_template(
                    'email/create_account.html',
                    firstname=user.firstname,
                    email=user.email,
                    password=password,
                    reset_link=UserService.get_reset_link(user)
                )
                mail.send(msg)
                app.logger.info(f"Account successfully created for user {user}")
            except IntegrityError:
                db.session.rollback()
                app.logger.warning(f"Account can't be created. User {user} already exists.")
            except SMTPException as e:
                db.session.rollback()
                app.logger.error(f"Account creation canceled for user {user}"
                                 f" because email could not be sent to {user.email}.")

    @staticmethod
    def get_user_allowed_years(user: User):
        if user.admin:
            return None, None
        user_promotion = user.promotion
        full_promotion_year = int('2' + user_promotion)
        starting_year = full_promotion_year - 3
        ending_year = starting_year + 3
        return starting_year, ending_year
    
    @staticmethod
    def has_basic_user_right_on_gallery(gallery, current_user: User):
        first_allowed_year, last_allowed_year = UserService.get_user_allowed_years(current_user)
        gallery_year = gallery.year.value
        if gallery_year >= first_allowed_year and gallery_year <= last_allowed_year:
            return True
        return False
