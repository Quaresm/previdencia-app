# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, request, redirect
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users
from .auth import is_valid_password, is_valid_email

views = Blueprint('views', __name__)
users = Users()

@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/config',  methods=['GET', 'POST'])
@login_required
def config():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        if len(email) > 255 or not is_valid_email(email):
            flash('Email inválido. Certifique-se de que seja válido e não pode haver mais de 255 caracteres.', category='error')
        elif not (6 <= len(username) <= 10):
            flash('O Usuário precisa ter no mínimo 6 caracteres ou exatamente 10 caracteres', category='error')
        else:
            update_user = users.update_user(username, email, current_user)
            if update_user == 'SucessfullUpdateUser':
                flash('Usuário atualizado com sucesso', category='success')
            else:
                flash('Falha ao atualizar o usuário', category='error')

            return render_template("users_page/config.html", user=current_user)
    return render_template("users_page/config.html", user=current_user)

@views.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if check_password_hash(current_user.password, new_password):
            flash('A nova senha não pode ser igual à senha atual', category='error')
        elif new_password != confirm_password:
            flash('As senhas precisam ser iguais', category='error')
        elif len(new_password) < 6:
            flash("A senha é muito curta", category='error')
        elif len(new_password) > 12:
            flash('A senha precisa ter até 12 caracteres', category='error')
        elif not is_valid_password(new_password):
            flash('A senha deve conter pelo menos letra maiúscula, letra minúscula, número, caractere especial e ser menor que 12 caracteres.', category='error')
        else:
            new_password_data = generate_password_hash(new_password)
            update_password_response = users.update_password(new_password_data, current_user.email)
            if update_password_response == 'SucessfullResetPassword':
                flash('Senha alterada com sucesso!', category='success')
                logout_user()
                return redirect('/login')
            else:
                flash('Falha ao redefinir a senha', category='error')
    return render_template('users_page/reset_password.html', user=current_user)