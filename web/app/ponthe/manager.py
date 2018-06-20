#!/bin/env python

from flask import Flask
from flask import jsonify
from flask_script import Manager

from ponthe import app
from ponthe import db
from ponthe.models import *

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
        #email="philippe.ferreira-de-sousa@eleves.enpc.fr"
    )
    user_ponthe = User(
        firstname="Ponthe",
        lastname="ENPC",
        username="ponthe.enpc",
        password="password",
        email="ponthe@liste.enpc.fr"
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
        private=False
    )
    event_coupe_de_l_X = Event(
        name="Coupe de l'X",
        author=user_ponthe,
        category=category_sports,
        private=False
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
        slug="jUpIiqdBWQ9VpXVMzgjV8cWiN6w0YBHMaklyjt8WrxlnBoMNzMTCFG",
        name="Hey !",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="jUpIiqdBWQ9VpXVMzgjV8cWiN6w0YBHMaklyjt8WrxlnBoMNzMTCFG.bmp"
    )
    file2 = File(
        type="IMAGE",
        slug="t3dn23iQCa4aEDu7nNXBBg9IyLZCzMSsmHHDHgCdB2b0eGI3sBOXhj",
        name="Keur",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="t3dn23iQCa4aEDu7nNXBBg9IyLZCzMSsmHHDHgCdB2b0eGI3sBOXhj.jpg"
    )
    file3 = File(
        type="IMAGE",
        slug="XbcoWxBD5PPzc941hXVMX1miFr5VSC6DuUtgGJRNARAYqn1tR38AoL",
        name="Champions du monde !",
        author=user_philippe,
        year=year_2016,
        event=event_admissibles,
        filename="XbcoWxBD5PPzc941hXVMX1miFr5VSC6DuUtgGJRNARAYqn1tR38AoL.jpg"
    )
    file4 = File(
        type="IMAGE",
        slug="EKMRZkewtLHvD01TQXrUmtwshEn0TJQLPZN3foQXPPLsP6DMcVOacN",
        name=None,
        author=user_philippe,
        year=year_2017,
        event=event_coupe_de_l_X,
        filename="EKMRZkewtLHvD01TQXrUmtwshEn0TJQLPZN3foQXPPLsP6DMcVOacN.bmp"
    )
    file5 = File(
        type="IMAGE",
        slug="8WsJH3V5D2nY3JxvkEJY8Xuv6RwJGS0AYaWipbp9vDB1zW69A5PR2n",
        name="Oh !",
        author=user_philippe,
        year=year_2017,
        event=event_coupe_de_l_X,
        filename="8WsJH3V5D2nY3JxvkEJY8Xuv6RwJGS0AYaWipbp9vDB1zW69A5PR2n.bmp"
    )

@manager.command
def load_fixtures():
    if input("Are you sure ? The database will be erased ! [y/N] ") in {"y", "Y", "yes", "Yes"}:
        print("Emptying database...")
        empty_db()
        print("Loading fixtures...")
        for fixture in list(Fixtures.__dict__.values())[1:-3]:
            print(fixture)
            db.session.add(fixture)
            db.session.commit()
    else:
        print("Exiting")


if __name__ == "__main__":
    manager.run()
