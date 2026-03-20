# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FloatField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, NumberRange
from wtforms.widgets import TextArea

class ProductForm(FlaskForm):
    """Form for adding/editing products"""
    title = StringField('Product Title', validators=[
        DataRequired(),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    price = FloatField('Price (MWK)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price must be positive')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=5000, message='Description must be between 10 and 5000 characters')
    ], widget=TextArea())
    images = FileField('Product Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!'),
    ], render_kw={'multiple': True})
    is_featured = BooleanField('Feature this product')
    seo_title = StringField('SEO Title', validators=[Optional(), Length(max=200)])
    seo_description = StringField('SEO Description', validators=[Optional(), Length(max=500)])

class MessageForm(FlaskForm):
    """Form for customer messages"""
    name = StringField('Your Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Your Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    message = TextAreaField('Your Message', validators=[
        DataRequired(),
        Length(min=5, max=2000, message='Message must be between 5 and 2000 characters')
    ], widget=TextArea())

class LoginForm(FlaskForm):
    """Owner login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class BusinessSettingsForm(FlaskForm):
    """Business settings form"""
    name = StringField('Business Name', validators=[DataRequired(), Length(max=100)])
    whatsapp = StringField('WhatsApp Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Business Email', validators=[DataRequired(), Email()])
    logo = FileField('Logo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg'])])
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = StringField('Meta Description', validators=[Optional(), Length(max=500)])
    google_analytics_id = StringField('Google Analytics ID', validators=[Optional(), Length(max=50)])
    facebook_pixel_id = StringField('Facebook Pixel ID', validators=[Optional(), Length(max=50)])
    email_notifications = BooleanField('Email Notifications')
    whatsapp_notifications = BooleanField('WhatsApp Notifications')
    daily_digest = BooleanField('Daily Digest')
