# app/commands.py
from flask import current_app
from app.utils.notifications import NotificationService
import click

def register_commands(app):
    @app.cli.command('send-digest')
    def send_digest_command():
        """Send daily digest emails"""
        with app.app_context():
            NotificationService.send_daily_digest()