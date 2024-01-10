# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash
from flask_login import current_user, login_required

views = Blueprint('views', __name__)

@views.route('/home')
@login_required
def home():
    return render_template("home.html")

@views.route('/config')
@login_required
def config():
    flash('Testesssssssssss', category='error')
    return render_template("config.html")