from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Document(db.Model):
    """Document model for PDF uploads and processing"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)

    # Source information
    source_type = db.Column(db.String(20), default='local')  # 'local' or 'google_drive'
    google_drive_id = db.Column(db.String(255), nullable=True)

    # Processing status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100

    # Metadata
    total_pages = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Error handling
    error_message = db.Column(db.Text, nullable=True)

    # Relationships
    summaries = db.relationship('Summary', backref='document', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Document {self.filename}>'

    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'source_type': self.source_type,
            'status': self.status,
            'progress': self.progress,
            'total_pages': self.total_pages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }


class Summary(db.Model):
    """Summary model for storing chapter and overall summaries"""
    __tablename__ = 'summaries'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)

    # Summary type and content
    summary_type = db.Column(db.String(20), nullable=False)  # 'chapter', 'overall'
    chapter_number = db.Column(db.Integer, nullable=True)
    chapter_title = db.Column(db.String(255), nullable=True)

    # Page range
    start_page = db.Column(db.Integer, nullable=True)
    end_page = db.Column(db.Integer, nullable=True)

    # Content
    content = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True)  # JSON array stored as text

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Summary {self.summary_type} for Document {self.document_id}>'

    def to_dict(self):
        """Convert summary to dictionary"""
        return {
            'id': self.id,
            'summary_type': self.summary_type,
            'chapter_number': self.chapter_number,
            'chapter_title': self.chapter_title,
            'start_page': self.start_page,
            'end_page': self.end_page,
            'content': self.content,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GoogleDriveToken(db.Model):
    """Store Google Drive OAuth tokens per user"""
    __tablename__ = 'google_drive_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # OAuth tokens
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GoogleDriveToken for User {self.user_id}>'
