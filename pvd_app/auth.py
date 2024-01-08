from flask import Blueprint, render_template, request, flash
from . import create_app
import bcrypt, os

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    data = request.form
    print(data)
    return render_template("login.html")

def is_valid_email(email):
    # Verifica se o e-mail contém '@' e '.com'
    return '@' in email and '.com' in email

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        if len(email) > 255 or not is_valid_email(email):
            flash('Email inválido. Certifique-se de que seja válido e não pode haver mais de 255 caracteres.', category='error')
        elif len(username) < 2:
            flash('Usuario precisa ser maior que 2 caracteres', category='error')
        elif password != confirm_password:
            flash('As senhas precisam ser iguais', category='error')
        elif len(password) < 8:
            flash('A senha precisa ser no minimo 8 caracteres', category='error')
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(hashed_password)
            flash('Acesso criado com sucesso', category='sucess')

    return render_template("sign_up.html")

@auth.route('/logout')
def logout():
    return "<p>Sair</p>"

