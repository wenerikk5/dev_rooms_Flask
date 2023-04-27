import os
from flask import current_app


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    FLASK_DEBUG = False
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', default='BAD_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = ''
    # Since SQLAlchemy 1.4.x has removed support for the 'postgres://' URI scheme,
    # update the URI to the postgres database to use the supported 'postgresql://' scheme
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'dbDev.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'rooms/static/uploads')


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    FLASK_DEBUG = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'dbTest.sqlite3')}"
    WTF_CSRF_ENABLED = False
