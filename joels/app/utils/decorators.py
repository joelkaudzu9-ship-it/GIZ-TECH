# app/utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from flask_login import current_user

def owner_required(f):
    """Decorator to require owner login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'owner_logged_in' not in session and not current_user.is_authenticated:
            flash('Please log in to access the dashboard.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def ajax_required(f):
    """Decorator to ensure request is AJAX"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid request'}), 400
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(limit=10, per=60):
    """Simple rate limiting decorator (use with Flask-Limiter for production)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implement your rate limiting logic here
            # This is a placeholder - use Flask-Limiter in production
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout=300):
    """Cache response decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implement caching logic here
            # This is a placeholder - use Flask-Caching in production
            return f(*args, **kwargs)
        return decorated_function
    return decorator