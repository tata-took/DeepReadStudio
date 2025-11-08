"""
WSGI configuration for PythonAnywhere deployment

Instructions:
1. Upload this file to your PythonAnywhere account
2. In the Web tab, point the WSGI configuration file to this file
3. Update the paths to match your PythonAnywhere directory structure
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/DeepReadStudio'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add backend directory
backend_path = os.path.join(project_home, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Import Flask app
from app import app as application

# Initialize database
with application.app_context():
    from models import db
    db.create_all()
