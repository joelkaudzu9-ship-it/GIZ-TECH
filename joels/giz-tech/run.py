# run.py
# !/usr/bin/env python
"""
GIZ-tech Portfolio Application
Entry point for running the application
"""
import os
import sys
from app import create_app

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get environment
env = os.getenv('FLASK_ENV', 'development')

# Create app
app = create_app(env)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))

    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(env == 'development')
    )