#!/bin/env python

from flask import Flask
from flask import jsonify
from flask_script import Manager

from ponthe import app
from ponthe import db
from ponthe.models import *
from ponthe.admin import views as admin_views
import subprocess, os

manager = Manager(app)

@manager.command
def empty_db():
    db.drop_all()
    db.create_all()

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
        admin=True,
        email_confirmed=False
    )

    category_sports = Category(
        name="Sports",
        author=user_philippe,
        description="Le sport c'est la vie"
    )
    category_vie_associative = Category(
        name="Vie associative",
        author=user_philippe,
        description="La meilleure vie associative de l'Est parisien !"
    )
    category_films = Category(
        name="Films",
        author=user_philippe,
        description="Tous plein de films ! Pour vous en mettre plein les yeux !"
    )
    category_voyages = Category(
        name="Voyages",
        author=user_philippe,
        description="Des voyages de oufs !"
    )

    event_admissibles = Event(
        name="Admissibles",
        author=user_philippe,
        category=category_vie_associative,
        private=False,
        description="Retour en enfance !"
    )
    event_coupe_de_l_X = Event(
        name="Coupe de l'X",
        author=user_ponthe,
        category=category_sports,
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
    file5 = File(
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
        for fixture in list(Fixtures.__dict__.values())[1:-3]:
            print(fixture)
            db.session.add(fixture)
            db.session.commit()
        print("Overwriting files...")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        subprocess.call(["rm", "-R", "../instance/club_folder"])
        subprocess.call(["cp", "-R", "../instance/test/", "../instance/club_folder"])

    else:
        print("Exiting")

@manager.command    # ponthe/manager.py batch_upload
def batch_upload():
    admin_views.batch_upload()


if __name__ == "__main__":
    manager.run()
