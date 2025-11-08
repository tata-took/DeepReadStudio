import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class"""

    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DATABASE_PATH', 'backend/deepread.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis & RQ
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')

    # Upload Settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 100))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'backend/uploads')
    ALLOWED_EXTENSIONS = {'pdf'}

    # Google Drive OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth2callback')
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # Authentication
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme')

    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
