from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user

from .models import User
from . import db
from .forms import RegistrationForm, LoginForm


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')

        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash('This username is already taken. Try another one.', 'warning')
            return render_template('main/register.html', form=form)

        user = User(username, password, name)

        db.session.add(user)
        db.session.commit()
        flash('You are now registered. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('main/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        existing_user = User.query.filter_by(username=username).first()

        if not (existing_user and existing_user.check_password(password)):
            flash('Incorrect credentials.', 'danger')
            return render_template('main/login.html', form=form)

        login_user(existing_user, remember=remember)
        flash(f'Welcome, {existing_user.name}', 'success')
        return redirect(url_for('main.profile', id=existing_user.id))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('main/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('main.index'))
