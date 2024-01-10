# -*- coding: utf-8 -*-
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from os import path
import os

dotenv_path = os.path.join(os.path.dirname(__file__), 'secret', '.env')
load_dotenv(dotenv_path)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    
    db.init_app(app)  
    migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    from .models import Users

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    login_manager.login_message = 'Por favor efetue o login'

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

#Setup for Sqlite
#create_database(app)

# DB_NAME = "database.db"
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
# def create_database(app):
#     if not path.exists('pvd_app/' + DB_NAME):
#         with app.app_context():  # Create a context
#             db.create_all()
#         print('Created Database!')