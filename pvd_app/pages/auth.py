# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, redirect, session
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from pvd_app.structure.models import Users
from pvd_app import create_app
import secrets
import os

auth = Blueprint('auth', __name__)
users = Users()

@auth.route('/')
def first_login():
    return redirect('/login')
@auth.route('/login', methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.get_user(email)

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                print(current_user)
                return redirect('/home')
            else:
                flash('Senha incorreta, tente novamente.', category='error')
        else:
            flash('Email não existe.', category='error')
            
    return render_template('pages/login.html')

def is_valid_email(email):
    # Verifica se o e-mail contém '@' e '.com'
    return '@' in email and '.com' in email

def is_valid_password(password):
    # Verifica se a senha atende aos critérios: pelo menos 1 letra maiúscula, 1 letra minúscula, 1 número, 1 caractere especial e menos de 12 caracteres
    return any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password) and any(c.isascii() and not c.isalnum() for c in password) and len(password) <= 12

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        user = users.get_user(email)

        if user != None:
            flash('Email já existe.', category='error')
        else:
            # Generate token
            token = users.generate_token(email)

            if len(email) > 255 or not is_valid_email(email):
                flash('Email inválido. Certifique-se de que seja válido e não pode haver mais de 255 caracteres.', category='error')
            elif not (6 <= len(username) <= 10):
                flash('O Usuário precisa ter no mínimo 8 caracteres ou exatamente 10 caracteres', category='error')
            elif password != confirm_password:
                flash('As senhas precisam ser iguais', category='error')
            elif len(password) < 6:
                flash("A senha é muito curta", category='error')
            elif len(password) > 12:
                flash('A senha precisa ter até 12 caracteres', category='error')
            elif not is_valid_password(password):
                flash('A senha deve conter pelo menos letra maiúscula, letra minúscula, número, caractere especial e ser menor que 12 caracteres.', category='error')
            else:  
                hashed_password = generate_password_hash(password)
                register_user = users.register_user(username, email, hashed_password, token)
                flash('Usuário registrado com sucesso!', category='success')
                return redirect('/login')
    return render_template("pages/sign_up.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

