#!/bin/env python
# coding=utf-8
import click, os

from . import app, db
from .file_helper import create_folder, copy_folder, delete_folders_in_folder,copy_folders_in_folder, copy_file
from .services import UserService


def _drop_and_recreate_db():
    click.echo("Emptying database...")
    if os.environ.get("TAG") == "master":
        app.logger.error("Environment variable TAG=master detected: you are on a production environment, database drop aborted")
        exit()
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
        create_folder("static")
        delete_folders_in_folder("static")
        copy_folder("test/uploads", "static/uploads")
        copy_data()
        copy_file("test/tmp/accounts.csv", "tmp/accounts.csv")
    else:
        app.logger.info("Abandon, exiting")


def persist_data():
    app.logger.info("Loading project data in database...")
    from ponthe.data.Data import Data
    for data in list(Data.__dict__.values())[1:-3]:
        app.logger.debug(data)
        db.session.add(data)
    db.session.commit()


def copy_data():
    app.logger.info("Copying files...")
    copy_folders_in_folder("../ponthe/data/galleries", "static/uploads")
    create_folder("static/thumbs")
    create_folder("tmp/uploads")


@app.cli.command(help="Load initial data of the app like categories")
def load_data():
    persist_data()
    os.chdir(app.instance_path)
    copy_data()


@app.cli.command(help="Create accounts based on accounts.csv in club_folder")
def create_accounts():
    csv_file = os.path.join(app.instance_path, 'tmp', 'accounts.csv')
    with open(csv_file, "r") as input:
        UserService.create_users(input)
