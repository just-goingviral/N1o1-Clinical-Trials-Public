"""
Authentication routes for Nitrite Dynamics application
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from models import db, User, ClinicalNote
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Define login and registration forms
class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    role = StringField('Role (doctor, researcher, admin)', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate username is unique"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """Validate email is unique"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')

# Create demo user if it doesn't exist
def create_demo_user():
    """Create demo user for demonstration purposes"""
    demo_user = User.query.filter_by(username='drbryandemo').first()
    if not demo_user:
        demo_user = User(
            username='drbryandemo',
            email='demo@n1o1dynamics.com',
            first_name='Nathan',
            last_name='Bryan',
            role='doctor'
        )
        demo_user.set_password('nitricoxide')
        db.session.add(demo_user)
        db.session.commit()
        print("Demo user created: drbryandemo / nitricoxide")
    return demo_user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # Check if already logged in
    if current_user.is_authenticated:
        # Use absolute URL to prevent potential loop
        return redirect(url_for('index', _external=True))
    
    # Create demo user if it doesn't exist
    demo_user = create_demo_user()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html', 
                                title='Sign In', 
                                form=form, 
                                demo_credentials={
                                    'username': demo_user.username,
                                    'password': 'nitricoxide'
                                })
        
        login_user(user, remember=form.remember_me.data)
        # Update last login time
        user.last_login = db.func.now()
        db.session.commit()
        
        next_page = request.args.get('next')
        # Validate that next is safe to prevent redirect loops
        if not next_page or not next_page.startswith('/') or next_page == url_for('auth.login'):
            next_page = url_for('index')
            
        # Use absolute URL for redirects
        return redirect(next_page)
    
    return render_template('auth/login.html', 
                          title='Sign In', 
                          form=form, 
                          demo_credentials={
                              'username': demo_user.username,
                              'password': 'nitricoxide'
                          })

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    # Use absolute URL to prevent potential loop
    return redirect(url_for('index', _external=True))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', title='Profile')