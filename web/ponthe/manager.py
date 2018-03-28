#!/bin/env python

from flask import Flask
from flask import jsonify
from flask_script import Manager

from ponthe import app
from ponthe import db

manager = Manager(app)

@manager.command
def load_fixtures():
    import glob
    from flask_fixtures.loaders import YAMLLoader
    from flask_fixtures import load_fixtures

    db.drop_all()
    db.create_all()

    for fixture_dir in app.config.get('FIXTURES_DIRS', ['./fixtures/']):
        for fixture_file in glob.glob(fixture_dir + '/*.yml'):
            fixtures = YAMLLoader().load(fixture_file)
            load_fixtures(db, fixtures)

if __name__ == "__main__":
    manager.run()
