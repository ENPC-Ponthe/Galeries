import os
from flask import Flask

def load(app: Flask):
    if os.environ.get('PROD_MODE') == 'true':
        app.logger.info("Galeries Ponthé starting in PROD mode")
        app.config.update(
            DEBUG = False,
            SECRET_KEY = os.environ['SECRET_KEY'],
            SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI'],
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            MAIL_SERVER = 'smtp.sparkpostmail.com',
            MAIL_PORT = 587,
            MAIL_USERNAME = 'SMTP_Injection',
            MAIL_PASSWORD = os.environ['MAIL_PASSWORD'],
            MAIL_USE_TLS = True,
            JWT_ALGORITHM = 'RS256',
            JWT_ACCESS_TOKEN_EXPIRES = False
        )
    else:
        app.logger.warn("Galeries Ponthé starting in DEV mode")
        app.config.from_pyfile('ponthe.cfg')

    with open(os.path.join(app.instance_path, "keys", "jwtRS256-public.pem"), 'r') as public_key:
        app.config['JWT_PUBLIC_KEY'] = public_key.read()
    with open(os.path.join(app.instance_path, "keys", "jwtRS256-private.pem"), 'r') as private_key:
        app.config['JWT_PRIVATE_KEY'] = private_key.read()
