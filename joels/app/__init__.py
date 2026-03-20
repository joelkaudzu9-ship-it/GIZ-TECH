import os
import secrets
from datetime import datetime
from flask import Flask, render_template
from dotenv import load_dotenv

from app.extensions import db, login_manager, migrate, cache, compress, csrf, limiter
from config import config

# Load environment variables
load_dotenv()


def register_template_filters(app):
    """Register custom Jinja2 filters"""

    @app.template_filter('from_json')
    def from_json_filter(value):
        """Convert JSON string to Python object"""
        try:
            import json
            return json.loads(value) if value else []
        except:
            return []

    @app.template_filter('split')
    def split_filter(value, separator=','):
        """Split a string by separator"""
        return value.split(separator) if value else []

    @app.template_filter('currency')
    def currency_filter(value):
        """Format as currency"""
        try:
            return f"MWK {value:,.2f}"
        except:
            return f"MWK {value}"

    @app.template_filter('truncate')
    def truncate_filter(text, length=100):
        """Truncate text to specified length"""
        if text and len(text) > length:
            return text[:length] + '...'
        return text

    @app.template_filter('time_ago')
    def time_ago_filter(date):
        """Convert datetime to 'time ago' format"""
        if not date:
            return ''

        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except:
                return date

        if not isinstance(date, datetime):
            return str(date)

        now = datetime.utcnow()
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)

        diff = now - date
        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours ago"
        elif seconds < 604800:
            return f"{int(seconds / 86400)} days ago"
        else:
            return date.strftime('%Y-%m-%d')

    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to <br> tags"""
        if not value:
            return ''
        return value.replace('\n', '<br>')


def register_context_processors(app):
    """Register context processors for all templates"""

    @app.context_processor
    def inject_now():
        """Inject current datetime into all templates"""
        return {'now': datetime.utcnow()}

    @app.context_processor
    def inject_unread_messages():
        """Inject unread messages count into all templates"""
        from app.models import Message

        def get_unread_count():
            try:
                from flask import session
                if session.get('owner_logged_in'):
                    return Message.query.filter_by(is_read=False).count()
            except:
                pass
            return 0

        return {'unread_messages': get_unread_count()}


def register_blueprints(app):
    """Register all blueprints"""

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/public/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('pages/public/500.html'), 500


def create_default_business():
    """Create default business if none exists"""
    from app.models import Business

    if Business.query.count() == 0:
        business = Business(
            name='GIZ-tech',
            whatsapp='265983142415',
            email='joelkaudzu9@gmail.com',
            meta_title='GIZ-tech - Premium Tech Products',
            meta_description='Discover premium tech products at GIZ-tech. Quality gadgets and electronics for tech enthusiasts.'
        )
        db.session.add(business)
        db.session.commit()
        print("✅ Default business created!")


def create_app(config_name=None):
    """Application factory function"""



    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__)

    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    # Load configuration
    app.config.from_object(config[config_name])

    # Set secret key if not set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(32)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)

    # Configure limiter
    limiter.init_app(app)

    # Register custom Jinja2 filters
    register_template_filters(app)

    # Register context processors
    register_context_processors(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # In create_app function, add:
    from app.commands import register_commands
    register_commands(app)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Create default business if none exists
        create_default_business()

    return app