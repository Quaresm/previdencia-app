# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, request, redirect, abort
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from pvd_app.structure.models import Users
from pvd_app import mail
from .auth import is_valid_password, is_valid_email
import secrets, hashlib
import urllib.parse

views = Blueprint('views', __name__)
users = Users()

@views.route('/home')
@login_required
def home():
    return render_template("pages/home.html", user=current_user)

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

            return render_template("user_page/config.html", user=current_user)
    return render_template("user_page/config.html", user=current_user)

@views.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    rota_atual = request.path
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        user_token = users.get_token(email)
        reset_url = f'http://localhost:5000/reset_password/{urllib.parse.quote(user_token)}'

        if current_user.is_authenticated == False:
            user = users.get_user(email)
            if user is None:
                flash('E-mail não encontrado na base de dados', category='error')
                return redirect('/reset_password')

            msg = Message('Reset de senha', recipients=[email])
            msg.body = f'Para resetar sua senha, clique no seguinte link: {reset_url}'
            mail.send(msg)
            flash('E-mail de reset enviado com sucesso', category='sucess')
            return redirect('/login')
        else:
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
    return render_template('user_page/reset_password.html', user=current_user, rota_atual=rota_atual)

@views.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    rota_atual = request.path
    user_email = users.get_user_email_by_token(token)
    if len(token) != 43:
        abort(404)
    if not users.confirm_token(token):
        abort(404)
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        token_confirmed = users.confirm_token(token)
        user_pass = users.get_user_pass_by_token(token)

        if token_confirmed:
            user = users.get_user(user_email)
            if user:
                if check_password_hash(user_pass, new_password):
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
                    update_password_response = users.update_password(new_password_data, user_email)
                    if update_password_response == 'SucessfullResetPassword':
                        flash('Senha alterada com sucesso!', category='success')
                        return redirect('/login')
                    else:
                        flash('Falha ao redefinir a senha', category='error')
    return render_template('user_page/reset_password.html',rota_atual=rota_atual, user_email=user_email)

@views.route('/simulate_pvd')
@login_required
def pre_simulation():
    data = [
        ("01-01-2024", 1234),
        ("02-01-2024", 1334),
        ("03-01-2024", 1234),
        ("04-01-2024", 1434),
        ("05-01-2024", 1534),
        ("06-01-2024", 1314),

    ]

    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    if labels and values:
        return render_template('pages/simulate_pvd.html', labels=labels, values=values)
    else:
        flash('Dados de simulação não encontrados.', category='error')
        return redirect('/home')