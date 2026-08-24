from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import current_user, login_user, logout_user

from app import bcrypt, db
from app.models import User


auth = Blueprint(
    'auth',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/app'
)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    # If already logged in, don't show login page
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):

        login_user(user, remember=True)

        return redirect(url_for('home.index'))

    flash('Invalid email or password!', 'danger')

    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():

    # If already logged in, don't show register page
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    if request.method == 'GET':
        return render_template('reg.html')

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    email_exist = User.query.filter_by(email=email).first()
    username_exist = User.query.filter_by(username=username).first()

    if len(username) <= 3:

        flash('Username is too short!', 'danger')
        return redirect(url_for('auth.register'))

    elif len(password) <= 3:

        flash('Password is too weak!', 'danger')
        return redirect(url_for('auth.register'))

    elif email_exist:

        flash('Email already in use', 'danger')
        return redirect(url_for('auth.register'))

    elif username_exist:

        flash('Username already in use', 'danger')
        return redirect(url_for('auth.register'))

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode('utf-8')

    user = User(
        username=username,
        password=hashed_password,
        email=email
    )

    db.session.add(user)
    db.session.commit()

    login_user(user, remember=True)

    return redirect(url_for('home.index'))


@auth.route('/logout')
def logout():

    logout_user()

    return redirect(url_for('auth.login'))