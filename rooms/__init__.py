import os
from babel.dates import format_datetime, format_timedelta
import click

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def create_app(config_filename=None):
    app = Flask(__name__)

    if config_filename:
        app.config.from_object(config_filename)
    else:
        config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
        app.config.from_object(config_type)

    initialise_extensions(app)
    register_blueprints(app)
    register_cli_commands(app)
    error_handlers(app)
    moment = Moment(app)
    custom_filters(app)

    with app.app_context():
        db.create_all()

    return app


def custom_filters(app):
    # @app.template_filter()
    # def datetime(value, format='medium'):
    #     if format == 'full':
    #         format="EEEE, d. MMMM y 'at' HH:mm"
    #     elif format == 'medium':
    #         format="EE dd.MM.y HH:mm"
    #     return format_datetime(value, format)
    #
    # from datetime import datetime
    # @app.template_filter()
    # def timesince(value):
    #     return format_timedelta(datetime.utcnow() - value)


    @app.template_filter()
    def length(value):
        return len(value)


def initialise_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    from rooms.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def register_blueprints(app):
    from rooms.auth import auth as auth_blueprint
    from rooms.main import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)


def register_cli_commands(app):
    from .commands import import_data_command
    app.cli.add_command(import_data_command)


def error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
