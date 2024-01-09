# -*- coding: utf-8 -*-
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os

db = SQLAlchemy()

DB_NAME = "database.db"

dotenv_path = os.path.join(os.path.dirname(__file__), 'secret', '.env')
load_dotenv(dotenv_path)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # Initialize extensions

    db.init_app(app)  

    from .views import views
    from .auth import auth

    from .models import Users

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    def login_required_message():
        return 'Você precisa estar autenticado para acessar esta página.'
    login_manager.login_required_message = login_required_message

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('pvd_app/' + DB_NAME):
        with app.app_context():  # Create a context
            db.create_all()
        print('Created Database!')