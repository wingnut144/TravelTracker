"""
Admin Module - Administrative functions and user management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, UserSettings, Trip, Flight, EmailAccount, EmailScanLog, UserRole
from auth import admin_required
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_trips': Trip.query.count(),
        'upcoming_trips': Trip.query.filter(Trip.start_date > datetime.utcnow()).count(),
        'total_flights': Flight.query.count(),
        'email_accounts': EmailAccount.query.filter_by(is_active=True).count(),
        'recent_scans': EmailScanLog.query.order_by(EmailScanLog.scan_time.desc()).limit(10).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@admin_required
def users():
    """User management"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) | 
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """User detail page"""
    user = User.query.get_or_404(user_id)
    
    # Get user statistics
    user_stats = {
        'trips': Trip.query.filter_by(user_id=user.id).count(),
        'upcoming_trips': Trip.query.filter(
            Trip.user_id == user.id,
            Trip.start_date > datetime.utcnow()
        ).count(),
        'email_accounts': EmailAccount.query.filter_by(user_id=user.id).count(),
        'last_login': user.last_login
    }
    
    return render_template('admin/user_detail.html', user=user, stats=user_stats)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user settings"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update user
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.is_active = request.form.get('is_active') == 'true'
        
        # Update role
        role = request.form.get('role')
        if role in ['user', 'admin']:
            user.role = UserRole.ADMIN if role == 'admin' else UserRole.USER
        
        # Update settings
        settings = user.user_settings
        settings.email_integration_enabled = request.form.get('email_integration') == 'true'
        settings.immich_integration_enabled = request.form.get('immich_integration') == 'true'
        settings.google_maps_enabled = request.form.get('google_maps') == 'true'
        
        try:
            db.session.commit()
            flash(f'User {user.username} updated successfully.', 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({
        'success': True,
        'message': f'User {user.username} {status}',
        'is_active': user.is_active
    })


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'User {username} deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/features')
@admin_required
def features():
    """Global feature management"""
    return render_template('admin/features.html')


@admin_bp.route('/features/toggle/<feature>', methods=['POST'])
@admin_required
def toggle_feature(feature):
    """Toggle a feature for all users"""
    enabled = request.form.get('enabled') == 'true'
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        # Apply to all users
        user_ids = [u.id for u in User.query.all()]
    
    count = 0
    
    for user_id in user_ids:
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if settings:
            if feature == 'email_integration':
                settings.email_integration_enabled = enabled
            elif feature == 'immich_integration':
                settings.immich_integration_enabled = enabled
            elif feature == 'google_maps':
                settings.google_maps_enabled = enabled
            count += 1
    
    db.session.commit()
    
    status = 'enabled' if enabled else 'disabled'
    flash(f'Feature {feature} {status} for {count} users.', 'success')
    
    return redirect(url_for('admin.features'))


@admin_bp.route('/email-logs')
@admin_required
def email_logs():
    """View email scan logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    logs = EmailScanLog.query.order_by(
        EmailScanLog.scan_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/email_logs.html', logs=logs)


@admin_bp.route('/trips')
@admin_required
def trips():
    """View all trips"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    search = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')
    
    query = Trip.query
    
    if search:
        query = query.filter(
            (Trip.title.ilike(f'%{search}%')) | 
            (Trip.destination.ilike(f'%{search}%'))
        )
    
    if filter_type == 'upcoming':
        query = query.filter(Trip.start_date > datetime.utcnow())
    elif filter_type == 'past':
        query = query.filter(Trip.end_date < datetime.utcnow())
    elif filter_type == 'auto_detected':
        query = query.filter_by(auto_detected=True)
    
    trips = query.order_by(Trip.start_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/trips.html', trips=trips, search=search, filter_type=filter_type)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """System settings"""
    if request.method == 'POST':
        # Update system settings (would store in database or config)
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html')


@admin_bp.route('/stats/overview')
@admin_required
def stats_overview():
    """Get overview statistics for dashboard"""
    now = datetime.utcnow()
    last_30_days = now - timedelta(days=30)
    
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'new_this_month': User.query.filter(User.created_at >= last_30_days).count(),
        },
        'trips': {
            'total': Trip.query.count(),
            'upcoming': Trip.query.filter(Trip.start_date > now).count(),
            'current': Trip.query.filter(
                Trip.start_date <= now,
                Trip.end_date >= now
            ).count(),
            'created_this_month': Trip.query.filter(Trip.created_at >= last_30_days).count(),
        },
        'flights': {
            'total': Flight.query.count(),
            'upcoming': Flight.query.filter(Flight.departure_time > now).count(),
        },
        'email': {
            'active_accounts': EmailAccount.query.filter_by(is_active=True).count(),
            'scans_today': EmailScanLog.query.filter(
                EmailScanLog.scan_time >= now.replace(hour=0, minute=0, second=0)
            ).count(),
        }
    }
    
    return jsonify(stats)


@admin_bp.route('/bulk-actions', methods=['POST'])
@admin_required
def bulk_actions():
    """Perform bulk actions on users"""
    action = request.form.get('action')
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        flash('No users selected.', 'warning')
        return redirect(url_for('admin.users'))
    
    count = 0
    
    if action == 'activate':
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user.id != current_user.id:
                user.is_active = True
                count += 1
        db.session.commit()
        flash(f'Activated {count} users.', 'success')
    
    elif action == 'deactivate':
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user.id != current_user.id:
                user.is_active = False
                count += 1
        db.session.commit()
        flash(f'Deactivated {count} users.', 'success')
    
    elif action == 'enable_email':
        for user_id in user_ids:
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            if settings:
                settings.email_integration_enabled = True
                count += 1
        db.session.commit()
        flash(f'Enabled email integration for {count} users.', 'success')
    
    elif action == 'disable_email':
        for user_id in user_ids:
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            if settings:
                settings.email_integration_enabled = False
                count += 1
        db.session.commit()
        flash(f'Disabled email integration for {count} users.', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/api-status')
@admin_required
def api_status():
    """View and manage API status"""
    from models import APIStatus
    from utils import check_airlabs_api_status
    
    # Get or create AirLabs status
    airlabs_status = APIStatus.query.filter_by(service_name='airlabs').first()
    
    if not airlabs_status:
        airlabs_status = APIStatus(service_name='airlabs')
        db.session.add(airlabs_status)
    
    # Check if we need to refresh (check monthly)
    from datetime import timedelta
    needs_refresh = (
        not airlabs_status.last_checked or 
        datetime.utcnow() - airlabs_status.last_checked > timedelta(days=30)
    )
    
    return render_template('admin/api_status.html', 
                         airlabs_status=airlabs_status,
                         needs_refresh=needs_refresh)

@admin_bp.route('/api-status/check/<service>')
@admin_required
def check_api_status(service):
    """Manually check API status"""
    from models import APIStatus
    from utils import check_airlabs_api_status
    
    if service == 'airlabs':
        result = check_airlabs_api_status()
        
        status = APIStatus.query.filter_by(service_name='airlabs').first()
        if not status:
            status = APIStatus(service_name='airlabs')
            db.session.add(status)
        
        status.is_active = result['status']
        status.last_checked = result['last_checked']
        status.status_message = result['message']
        db.session.commit()
        
        flash(f"AirLabs API: {result['message']}", 'success' if result['status'] else 'danger')
    
    return redirect(url_for('admin.api_status'))

def init_admin(app):
    """Initialize admin module"""
    app.register_blueprint(admin_bp)
