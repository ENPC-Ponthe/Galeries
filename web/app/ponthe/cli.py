#!/bin/env python
# coding=utf-8
import click, os, subprocess, csv, glob

from flask import render_template
from flask_mail import Message
from smtplib import SMTPException

from sqlalchemy.exc import IntegrityError

from . import app, mail, db
from .file_helper import create_folder, delete_folder, copy_folder, delete_folders_in_folder,copy_folders_in_folder, copy_file
from .models import User
from .services import UserService, GalleryService


def _drop_and_recreate_db():
    click.echo("Emptying database...")
    db.drop_all()
    db.create_all()


@app.cli.command(help='Empty database.')
def empty_db():
    _drop_and_recreate_db()


@app.cli.command(help="Load fixtures")
def load_fixtures():
    click.echo("NEVER DO THIS IN PRODUCTION !!!")
    if click.confirm("Are you sure ? The database and the files will be erased !"):
        _drop_and_recreate_db()
        app.logger.info("Loading fixtures...")
        persist_data()
        from ponthe.data.Fixtures import Fixtures
        for fixture in list(Fixtures.__dict__.values())[1:-3]:
            app.logger.debug(fixture)
            db.session.add(fixture)
        db.session.commit()
        app.logger.info("Overwriting files...")
        os.chdir(app.instance_path)
        # Can't rm club_folder in docker because a volume is mounted on it : busy
        create_folder("club_folder")
        delete_folder("club_folder/waiting_zone")
        create_folder("upload_tmp")
        delete_folders_in_folder("uploads")
        delete_folders_in_folder("thumbs")
        copy_folder("test/club_folder/waiting_zone", "club_folder/waiting_zone")
        copy_folders_in_folder("test/uploads", "uploads")
        copy_data()
        copy_file("test/club_folder/accounts.csv", "club_folder/accounts.csv")
    else:
        app.logger.info("Abandon, exiting")


@app.cli.command(help="Mass import from waiting zone")
def batch_upload():
    GalleryService.batch_upload(None)


def persist_data():
    app.logger.info("Loading project data in database...")
    from ponthe.data.Data import Data
    for data in list(Data.__dict__.values())[1:-3]:
        app.logger.debug(data)
        db.session.add(data)
    db.session.commit()


def copy_data():
    app.logger.info("Copying files...")
    copy_folders_in_folder("../ponthe/data/galleries", "uploads")


@app.cli.command(help="Load initial data of the app like categories")
def load_data():
    persist_data()
    os.chdir(app.instance_path)
    copy_data()


@app.cli.command(help="Create accounts based on accounts.csv in club_folder")
def create_accounts():
    csv_file = os.path.join(app.instance_path, 'club_folder', 'accounts.csv')
    with open(csv_file, "r") as input:
        csv_reader = csv.reader(input)
        for gender, lastname, firstname, email, origin, department, promotion in csv_reader:
            user = User(firstname=firstname, lastname=lastname, gender=gender, origin=origin, department=department, promotion=promotion, email=email, admin=False, email_confirmed=True)
            password = User.generate_random_password()
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
                msg = Message('Bienvenue aux Ponts', sender='Ponthé <no-reply@ponthe.enpc.org>',
                              recipients=[user.email])
                msg.body = 'Ton club d\'audiovisuel te souhaite la bienvenue aux Ponts ! '\
                    + 'Ton compte Ponthé a été créé sur https://ponthe-testing.enpc.org. '\
                    + 'Connecte-toi dès maintenant avec les identifiants suivants :\n'\
                    + 'Email : {}\n'.format(user.email)\
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
