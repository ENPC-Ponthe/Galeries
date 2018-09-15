#!/bin/env python

from flask import Flask, render_template
from flask_mail import Message
from flask_script import Manager

from ponthe import app, mail
from ponthe import db
from ponthe.file_helper import create_folder, delete_folder, copy_folder
from ponthe.models import *
from ponthe.admin import views as admin_views
import os, subprocess, csv

from sparkpost import SparkPostException
from sqlalchemy.exc import IntegrityError

manager = Manager(app)

@manager.command
def empty_db():
    db.drop_all()
    db.create_all()

class Data():
    category_sports = Category(
        name="Sports",
        description="Le sport c'est la vie"
    )
    category_vie_associative = Category(
        name="Vie associative",
        description="La meilleure vie associative de l'Est parisien !"
    )
    category_films = Category(
        name="Films",
        description="Tous plein de films ! Pour vous en mettre plein les yeux !"
    )
    category_voyages = Category(
        name="Voyages",
        description="Des voyages de oufs !"
    )

class Fixtures():
    user_philippe = User(
        firstname="Philippe",
        lastname="Ferreira De Sousa",
        username="philippe.ferreira-de-sousa",
        password="password",
        admin=True,
        email_confirmed=True
    )
    user_ponthe = User(
        firstname="Ponthe",
        lastname="ENPC",
        username="ponthe.enpc",
        password="password",
        email="ponthe@liste.enpc.fr",
        admin=False,
        email_confirmed=True
    )

    event_admissibles = Event(
        name="Admissibles",
        author=user_philippe,
        category=Data.category_vie_associative,
        private=False,
        description="Retour en enfance !"
    )
    event_coupe_de_l_X = Event(
        name="Coupe de l'X",
        author=user_ponthe,
        category=Data.category_sports,
        private=False,
        description="Tournoi sportif majeur de la vie des écoles d'ingénieur ! Et les Ponts ont fait pas mal de perf' !"
    )

    year_2016 = Year(
        slug="2016",
        name="Une année riche en victoires !",
        author=user_philippe,
        value=2016
    )
    year_2017= Year(
        slug="2017",
        name="Une année de folie !",
        author=user_philippe,
        value=2017
    )

    file1 = File(
        type="IMAGE",
        slug="jUpIiqdBWQ9VpXVMzgjV",
        name="Hey !",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="jUpIiqdBWQ9VpXVMzgjV.bmp",
        pending=False
    )
    file2 = File(
        type="IMAGE",
        slug="t3dn23iQCa4aEDu7nNXB",
        name="Keur",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="t3dn23iQCa4aEDu7nNXB.jpg",
        pending=False
    )
    file3 = File(
        type="IMAGE",
        slug="XbcoWxBD5PPzc941hXVM",
        name="Champions du monde !",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="XbcoWxBD5PPzc941hXVM.jpg",
        pending=True
    )
    file4 = File(
        type="IMAGE",
        slug="EKMRZkewtLHvD01TQXrU",
        name=None,
        author=user_philippe,
        year=year_2017,
        event=event_coupe_de_l_X,
        filename="EKMRZkewtLHvD01TQXrU.jpg",
        pending=False
    )
    file5 = File(
        type="IMAGE",
        slug="8WsJH3V5D2nY3JxvkEJY",
        name="Oh !",
        author=user_philippe,
        year=year_2017,
        event=event_coupe_de_l_X,
        filename="8WsJH3V5D2nY3JxvkEJY.png",
        pending=True
    )
    file6 = File(
        type="IMAGE",
        slug="b4iryeMgCfPsN7Egq8Z9",
        name="Bouilla !",
        author=user_ponthe,
        year=year_2017,
        event=event_coupe_de_l_X,
        filename="b4iryeMgCfPsN7Egq8Z9.jpg",
        pending=True
    )

@manager.command    # ponthe/manager.py load_fixtures
def load_fixtures():
    print("NEVER DO THIS IN PRODUCTION !!!")
    if input("Are you sure ? The database and the files will be erased ! [y/N] ") in {"y", "Y", "yes", "Yes"}:
        print("Emptying database...")
        empty_db()
        print("Loading fixtures...")
        load_data()
        for fixture in list(Fixtures.__dict__.values())[1:-3]:
            print(fixture)
            db.session.add(fixture)
            db.session.commit()
        print("Overwriting files...")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # Can't rm club_folder in docker because a volume is mounted on it : busy
        create_folder("../instance/club_folder")
        create_folder("../instance/upload_tmp")
        delete_folder("../instance/club_folder/waiting_zone")
        delete_folder("../instance/club_folder/uploads")
        copy_folder("../instance/test/waiting_zone", "../instance/club_folder/waiting_zone")
        copy_folder("../instance/test/uploads", "../instance/club_folder/uploads")
        subprocess.call(["cp", "../instance/test/accounts.csv", "../instance/club_folder/"])
    else:
        print("Abandon, exiting")

@manager.command    # ponthe/manager.py batch_upload
def batch_upload():
    admin_views.batch_upload()

@manager.command
def load_data():
    #categories = [Fixtures.category_sports, Fixtures.category_vie_associative, Fixtures.category_films, Fixtures.category_voyages]
    for category in list(Data.__dict__.values())[1:-3]:
        print(category)
        db.session.add(category)
        db.session.commit()

@manager.command
def create_accounts():
    csv_file = os.path.join(app.instance_path, 'club_folder', 'accounts.csv')
    with open(csv_file, "r") as input:
        csv_reader = csv.reader(input)

        for gender, lastname, firstname, email, origin, department, promotion in csv_reader:

            user = User(firstname=firstname, lastname=lastname, email=email, admin=False, email_confirmed=True)
            password = User.generate_random_password()
            user.set_password(password)
            print(user)
            db.session.add(user)
            try:
                db.session.commit()
                msg = Message('Bienvenue aux Ponts', sender='Ponthé <no-reply@ponthe.enpc.org>',
                              recipients=[user.email])
                msg.body = 'Ton club d\'audiovisuel te souhaite la bienvenue aux Ponts ! '\
                    + 'Ton compte Ponthé a été créé sur https://ponthe.enpc.org. '\
                    + 'Connecte-toi dès maintenant avec les identifiants suivants :\n'\
                    + 'Email : {}\n'.format(user.email)\
                    + 'Mot de passe : {}'.format(password)
                msg.html = render_template('email/create_account.html', firstname=user.firstname, email=user.email, password=password)
                mail.send(msg)
            except IntegrityError:
                db.session.rollback()
                print("User already exists")
            except SparkPostException as e:
                db.session.rollback()
                print("Email could not be sent")
                raise e


if __name__ == "__main__":
    manager.run()
