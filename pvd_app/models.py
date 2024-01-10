# -*- coding: utf-8 -*-
from flask_login import UserMixin
from pvd_app import db

class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(170))

    def register_user(self, username, email, password):
        user = Users.query.filter_by(email=email).first()

        if user:
            return 'User has been registred'
        else:
            new_user = Users(username=username, email=email, password=password)

            db.session.add(new_user)
            db.session.commit()

            check_user = Users.query.filter_by(email=email).first()

    def update_user(self, username, email, password):
        user = Users.query.filter_by(email=email).first()

        if user:
            user.username = username
            user.email = email
            user.password = password

            db.session.commit()
            return 'SucessfullUpdateUser'
        else:
            return 'FailedUpdateUser'

    def get_all_users(self):
        return Users.query.order_by(Users.username).all()
    def get_user(self, email):
        return Users.query.filter_by(email=email).first()