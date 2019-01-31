
import os
from flask import Flask


class Constants:
    AVAILABLE_PROMOTIONS = ["022", "021", "020", "019", "018"]
    LAST_PROMOTION = "022"


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
            JWT_ACCESS_TOKEN_EXPIRES = False,
            CAS_SERVER = 'https://cas.enpc.fr',
            CAS_AFTER_LOGIN = 'public.cas',
        )
    else:
        app.logger.warning("Galeries Ponthé starting in DEV mode")
        app.config.from_pyfile('ponthe.cfg')
    with open(os.path.join(app.instance_path, "keys", "jwtRS256-public.pem"), 'r') as public_key:
        app.config['JWT_PUBLIC_KEY'] = public_key.read()
    with open(os.path.join(app.instance_path, "keys", "jwtRS256-private.pem"), 'r') as private_key:
        app.config['JWT_PRIVATE_KEY'] = private_key.read()
    app.config['ASSET_ROOT'] = os.path.join(app.instance_path, 'assets')
    app.config['UPLOAD_TMP_ROOT'] = os.path.join(app.instance_path, 'tmp', 'uploads')

    # Flask-Thumbnail configuration
    app.config['MEDIA_ROOT'] = os.path.join(app.instance_path, 'static', 'uploads')
    app.config['THUMBNAIL_MEDIA_ROOT'] = app.config['MEDIA_ROOT']
    app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'] = os.path.join(app.instance_path, 'static', 'thumbs')
    app.config['THUMBNAIL_MEDIA_THUMBNAIL_URL'] = '/thumbs'
