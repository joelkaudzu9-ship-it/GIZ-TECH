# app/models.py
import json
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager
import secrets


class Business(db.Model):
    """Single business/owner model"""
    __tablename__ = 'business'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='GIZ-tech')
    whatsapp = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    logo = db.Column(db.String(200))
    favicon = db.Column(db.String(200))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    google_analytics_id = db.Column(db.String(50))
    facebook_pixel_id = db.Column(db.String(50))
    email_notifications = db.Column(db.Boolean, default=True)
    whatsapp_notifications = db.Column(db.Boolean, default=False)
    daily_digest = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def to_dict(self):
        return {
            'name': self.name,
            'whatsapp': self.whatsapp,
            'email': self.email,
            'logo': self.logo,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description
        }


class Subscriber(db.Model):
    __tablename__ = 'subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Subscriber {self.email}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text, default='[]')  # JSON array of image paths
    thumbnail = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    is_sold = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    date_sold = db.Column(db.DateTime)
    last_viewed = db.Column(db.DateTime)

    # Relationships
    messages = db.relationship('Message', backref='product', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug:
            self.generate_slug()

    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        if self.title:
            # Convert to lowercase, replace spaces with hyphens, remove special chars
            self.slug = secrets.token_urlsafe(8) + '-' + '-'.join(
                word for word in self.title.lower().split() if word.isalnum()
            )[:50]

    @property
    def image_list(self):
        """Get list of image paths from JSON"""
        try:
            return json.loads(self.images) if self.images else []
        except:
            return []

    @image_list.setter
    def image_list(self, images):
        """Set images as JSON"""
        self.images = json.dumps(images)

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.last_viewed = datetime.utcnow()
        db.session.commit()

    def mark_sold(self):
        """Mark product as sold"""
        self.is_sold = True
        self.date_sold = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'price': self.price,
            'description': self.description[:200] + '...' if len(self.description) > 200 else self.description,
            'thumbnail': self.thumbnail or (self.image_list[0] if self.image_list else None),
            'images': self.image_list,
            'views': self.views,
            'is_sold': self.is_sold,
            'is_featured': self.is_featured,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None
        }

    def __repr__(self):
        return f'<Product {self.title}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'is_read': self.is_read,
            'product': self.product.title if self.product else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Message from {self.name} for {self.product.title if self.product else "Unknown"}>'


class Owner(UserMixin, db.Model):
    """Owner authentication model"""
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Owner {self.username}>'


# app/models.py - Update Activity class

class Activity(db.Model):
    """Track user activities for analytics"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))  # view, message, sold, etc.
    entity_type = db.Column(db.String(50))  # product, message
    entity_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary with proper date handling"""
        return {
            'id': self.id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_at_obj': self.created_at  # Keep original for template
        }


@login_manager.user_loader
def load_user(user_id):
    return Owner.query.get(int(user_id))