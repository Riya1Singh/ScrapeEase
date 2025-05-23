from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models import User, db
from bcrypt import hashpw, gensalt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if the form is for registration
        if 'email' in request.form:
            # Register form handling
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            agree = request.form.get('agree')

            if not agree:
                flash('You must agree to the Terms and Conditions')
                return redirect(url_for('auth.login'))

            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('auth.login'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('auth.login'))

            hashed_password = hashpw(password.encode('utf-8'), gensalt())
            new_user = User(
                username=username, 
                password=hashed_password.decode('utf-8'), 
                email=email
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please login')
            return redirect(url_for('auth.login'))
        
        else:
            # Login form handling
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()

            if user and hashpw(password.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):            
                login_user(user, remember=remember)
                return redirect(url_for('home'))  # Redirect to your home page

            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
