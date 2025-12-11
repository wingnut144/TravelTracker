"""
Authentication module for Travel Tracking System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, UserSettings, UserRole
from functools import wraps
import requests
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access"""
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login'))

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Create default user settings
        user_settings = UserSettings(user=user)
        
        db.session.add(user)
        db.session.add(user_settings)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/google')
def google_auth():
    """Initiate Google OAuth"""
    from app import app
    
    if not app.config['GOOGLE_CLIENT_ID']:
        flash('Google integration is not configured.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Build OAuth URL
    oauth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={app.config["GOOGLE_CLIENT_ID"]}&'
        f'redirect_uri={app.config["GOOGLE_REDIRECT_URI"]}&'
        'response_type=code&'
        'scope=openid email profile https://www.googleapis.com/auth/gmail.readonly&'
        'access_type=offline&'
        'prompt=consent'
    )
    
    return redirect(oauth_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    from app import app
    
    code = request.args.get('code')
    if not code:
        flash('Google authentication failed.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Exchange code for token
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': app.config['GOOGLE_REDIRECT_URI'],
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        tokens = response.json()
        
        if 'error' in tokens:
            flash('Failed to authenticate with Google.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        # Store in session for linking to account
        session['oauth_provider'] = 'google'
        session['oauth_tokens'] = tokens
        session['oauth_email'] = userinfo['email']
        
        if current_user.is_authenticated:
            # Link to existing account
            return redirect(url_for('settings.link_email_account'))
        else:
            flash('Google authentication successful. Please log in or register.', 'info')
            return redirect(url_for('auth.login'))
    
    except Exception as e:
        flash(f'Error during Google authentication: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/microsoft')
def microsoft_auth():
    """Initiate Microsoft OAuth"""
    from app import app
    
    if not app.config['MICROSOFT_CLIENT_ID']:
        flash('Microsoft integration is not configured.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Build OAuth URL
    oauth_url = (
        'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?'
        f'client_id={app.config["MICROSOFT_CLIENT_ID"]}&'
        f'redirect_uri={app.config["MICROSOFT_REDIRECT_URI"]}&'
        'response_type=code&'
        'scope=openid email profile Mail.Read offline_access&'
        'response_mode=query'
    )
    
    return redirect(oauth_url)

@auth_bp.route('/microsoft/callback')
def microsoft_callback():
    """Handle Microsoft OAuth callback"""
    from app import app
    
    code = request.args.get('code')
    if not code:
        flash('Microsoft authentication failed.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Exchange code for token
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    data = {
        'code': code,
        'client_id': app.config['MICROSOFT_CLIENT_ID'],
        'client_secret': app.config['MICROSOFT_CLIENT_SECRET'],
        'redirect_uri': app.config['MICROSOFT_REDIRECT_URI'],
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        tokens = response.json()
        
        if 'error' in tokens:
            flash('Failed to authenticate with Microsoft.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user info
        userinfo_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        # Store in session for linking to account
        session['oauth_provider'] = 'outlook'
        session['oauth_tokens'] = tokens
        session['oauth_email'] = userinfo.get('mail') or userinfo.get('userPrincipalName')
        
        if current_user.is_authenticated:
            # Link to existing account
            return redirect(url_for('settings.link_email_account'))
        else:
            flash('Microsoft authentication successful. Please log in or register.', 'info')
            return redirect(url_for('auth.login'))
    
    except Exception as e:
        flash(f'Error during Microsoft authentication: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

def init_auth(app):
    """Initialize authentication"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    app.register_blueprint(auth_bp)
