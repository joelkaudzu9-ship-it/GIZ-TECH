# app/utils/file_handler.py
import os
import secrets
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
import uuid


class FileHandler:
    """File handling without Pillow dependencies"""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def allowed_file(filename, file_types=None):
        """Check if file extension is allowed"""
        if file_types is None:
            file_types = FileHandler.ALLOWED_EXTENSIONS

        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in file_types

    @staticmethod
    def get_unique_filename(original_filename):
        """Generate unique filename with timestamp and random string"""
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        timestamp = int(datetime.utcnow().timestamp())
        random_str = secrets.token_hex(8)
        unique_name = f"{timestamp}_{random_str}"

        if ext:
            unique_name = f"{unique_name}.{ext}"

        return unique_name

    @staticmethod
    def save_images(files, subfolder='products'):
        """Save multiple images without optimization"""
        saved_images = []

        # Create subfolder path
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_folder, exist_ok=True)

        for file in files:
            if file and FileHandler.allowed_file(file.filename):
                try:
                    # Secure filename and get unique name
                    filename = FileHandler.get_unique_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)

                    # Save file
                    file.save(filepath)

                    # Return the path
                    saved_images.append(f"/static/uploads/{subfolder}/{filename}")

                except Exception as e:
                    current_app.logger.error(f"Failed to save file {file.filename}: {e}")

        return saved_images

    @staticmethod
    def delete_image(filepath):
        """Safely delete image"""
        try:
            # Convert URL path to filesystem path
            if filepath.startswith('/static/'):
                filepath = filepath.replace('/static/', '')

            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)

            # Delete main image
            if os.path.exists(full_path):
                os.remove(full_path)

            return True
        except Exception as e:
            current_app.logger.error(f"Failed to delete image: {e}")
            return False

    @staticmethod
    def optimize_image(filepath, max_width=1920, max_height=1080, quality=85):
        """Placeholder - returns filename without optimization"""
        return os.path.basename(filepath)

    @staticmethod
    def create_thumbnail(filepath, size=(300, 300)):
        """Placeholder - returns None (no thumbnail)"""
        return None