# fix_blueprints.py
import os

# Template for __init__.py files
INIT_TEMPLATE = '''from flask import Blueprint

bp = Blueprint('{name}', __name__)

from app.{name} import routes
'''

# Template for routes.py files
ROUTES_TEMPLATE = '''from flask import render_template, request, jsonify, current_app, session, abort
from app.{name} import bp
from app.models import Product, Business, Message, Activity
from app.extensions import db, cache, limiter
from app.forms import MessageForm
from app.utils.file_handler import FileHandler
from app.utils.validators import sanitize_input
from datetime import datetime
import json

@bp.route('/')
def index():
    """Placeholder route - replace with actual routes"""
    return "{} blueprint working".format("{name}")
'''

# Fix each blueprint
for blueprint in ['main', 'auth', 'dashboard', 'api']:
    init_path = f'app/{blueprint}/__init__.py'
    routes_path = f'app/{blueprint}/routes.py'

    # Write __init__.py
    with open(init_path, 'w') as f:
        f.write(INIT_TEMPLATE.format(name=blueprint))
    print(f"✅ Fixed {init_path}")

    # Check if routes.py exists, create placeholder if not
    if not os.path.exists(routes_path):
        with open(routes_path, 'w') as f:
            f.write(ROUTES_TEMPLATE.format(name=blueprint))
        print(f"✅ Created {routes_path}")
    else:
        # Read existing routes.py to check imports
        with open(routes_path, 'r') as f:
            content = f.read()

        # Add blueprint import if missing
        if f"from app.{blueprint} import bp" not in content:
            # This is a simplified fix - you may need to manually adjust
            print(f"⚠️  Please check {routes_path} - add: from app.{blueprint} import bp")

print("\n🎯 Done! Now try running: python run.py")