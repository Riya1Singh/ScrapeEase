from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models import User, db
from bcrypt import hashpw, gensalt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        new_user = User(username=username, password=hashed_password.decode('utf-8'), email=email)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()

        if user and hashpw(password.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
            login_user(user)
            return redirect(url_for('protected'))  # Redirect to your home page

        flash('Invalid username or password')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
