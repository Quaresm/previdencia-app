# -*- coding: utf-8 -*-
from flask_login import UserMixin
from pvd_app import db
from sqlalchemy import text
import secrets

class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(170))
    token = db.Column(db.String(50))

    def register_user(self, username, email, password, token):
        user = Users.query.filter_by(email=email).first()

        if user:
            return 'User has been registred'
        else:
            new_user = Users(username=username, email=email, password=password, token=token)

            db.session.add(new_user)
            db.session.commit()

            check_user = Users.query.filter_by(email=email).first()

    def update_user(self, username, email, current_user):
        drop_constraint_sql = text("ALTER TABLE users DROP CONSTRAINT users_email_key")
        db.session.execute(drop_constraint_sql)
        user = Users.query.filter_by(email=current_user.email).first()

        if user:
            user.username = username
            user.email = email

            add_constraint_sql = text("ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email)")
            db.session.execute(add_constraint_sql)
            db.session.commit()
            return 'SucessfullUpdateUser'
        else:
            return 'FailedUpdateUser'

    def update_password(self, password, email):
        user = Users.query.filter_by(email=email).first()

        if user:
            user.password = password

            db.session.commit()

            return 'SucessfullResetPassword'
        else:
            return 'FailedtoResetPassword'

    def get_all_users(self):
        return Users.query.order_by(Users.username).all()
    def get_user(self, email):
        return Users.query.filter_by(email=email).first()
    def get_token(self, email):
        user = Users.query.filter_by(email=email).first()
        if user:
            return user.token
        return None

    #Functions for a user not authenticated // * //
    def confirm_token(self, token):
        return Users.query.filter_by(token=token).first()
    def get_user_email_by_token(self, token):
        user_email = Users.query.filter_by(token=token).value(text('email'))
        return user_email
    def get_user_pass_by_token(self, token):
        user_pass = Users.query.filter_by(token=token).value(text('password'))
        return user_pass
    # // * //
    def generate_token(self, email):
        token = secrets.token_urlsafe(32)
        user = Users.query.filter_by(email=email).first()
        if user:
            user.token = token
            db.session.commit()
        return token