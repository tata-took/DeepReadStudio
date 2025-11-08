import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime

from config import Config
from models import db, User, Document, Summary, GoogleDriveToken
from utils.google_drive import GoogleDriveClient
from tasks import process_document_task

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize extensions
CORS(app, supports_credentials=True)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Authentication Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user.id, 'username': user.username}
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {'id': current_user.id, 'username': current_user.username}
        }), 200
    return jsonify({'authenticated': False}), 200


# Document Upload Routes
@app.route('/api/upload/local', methods=['POST'])
@login_required
def upload_local():
    """Upload PDF from local storage"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only PDF files are accepted'}), 400

    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Save file
        file.save(file_path)

        # Calculate hash
        file_hash = calculate_file_hash(file_path)

        # Check if file already exists
        existing_doc = Document.query.filter_by(file_hash=file_hash).first()
        if existing_doc:
            os.remove(file_path)  # Remove duplicate
            return jsonify({
                'message': 'File already exists',
                'document': existing_doc.to_dict()
            }), 200

        # Get file size
        file_size = os.path.getsize(file_path)

        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=filename,
            file_hash=file_hash,
            file_path=file_path,
            file_size=file_size,
            source_type='local',
            status='pending'
        )

        db.session.add(document)
        db.session.commit()

        # Enqueue processing task
        from tasks import enqueue_document_processing
        job = enqueue_document_processing(document.id)

        return jsonify({
            'message': 'File uploaded successfully',
            'document': document.to_dict(),
            'job_id': job.id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/google-drive', methods=['POST'])
@login_required
def upload_google_drive():
    """Upload PDF from Google Drive"""
    data = request.get_json()
    file_id = data.get('file_id')

    if not file_id:
        return jsonify({'error': 'Google Drive file ID required'}), 400

    try:
        # Get Google Drive token
        token_record = GoogleDriveToken.query.filter_by(user_id=current_user.id).first()
        if not token_record:
            return jsonify({'error': 'Google Drive not authorized'}), 401

        # Download file from Google Drive
        drive_client = GoogleDriveClient(token_record)
        file_info = drive_client.download_file(file_id, app.config['UPLOAD_FOLDER'])

        # Calculate hash
        file_hash = calculate_file_hash(file_info['path'])

        # Check if file already exists
        existing_doc = Document.query.filter_by(file_hash=file_hash).first()
        if existing_doc:
            os.remove(file_info['path'])  # Remove duplicate
            return jsonify({
                'message': 'File already exists',
                'document': existing_doc.to_dict()
            }), 200

        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=file_info['name'],
            file_hash=file_hash,
            file_path=file_info['path'],
            file_size=file_info['size'],
            source_type='google_drive',
            google_drive_id=file_id,
            status='pending'
        )

        db.session.add(document)
        db.session.commit()

        # Enqueue processing task
        from tasks import enqueue_document_processing
        job = enqueue_document_processing(document.id)

        return jsonify({
            'message': 'File downloaded from Google Drive successfully',
            'document': document.to_dict(),
            'job_id': job.id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Google Drive OAuth Routes
@app.route('/api/google-drive/auth-url', methods=['GET'])
@login_required
def get_google_drive_auth_url():
    """Get Google Drive OAuth authorization URL"""
    try:
        drive_client = GoogleDriveClient()
        auth_url = drive_client.get_authorization_url()
        return jsonify({'auth_url': auth_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/google-drive/callback', methods=['POST'])
@login_required
def google_drive_callback():
    """Handle Google Drive OAuth callback"""
    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({'error': 'Authorization code required'}), 400

    try:
        drive_client = GoogleDriveClient()
        credentials = drive_client.exchange_code(code)

        # Store or update token
        token_record = GoogleDriveToken.query.filter_by(user_id=current_user.id).first()

        if token_record:
            token_record.access_token = credentials.token
            token_record.refresh_token = credentials.refresh_token
            token_record.token_expiry = credentials.expiry
            token_record.updated_at = datetime.utcnow()
        else:
            token_record = GoogleDriveToken(
                user_id=current_user.id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry
            )
            db.session.add(token_record)

        db.session.commit()

        return jsonify({'message': 'Google Drive authorized successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/google-drive/files', methods=['GET'])
@login_required
def list_google_drive_files():
    """List PDF files from Google Drive"""
    try:
        token_record = GoogleDriveToken.query.filter_by(user_id=current_user.id).first()
        if not token_record:
            return jsonify({'error': 'Google Drive not authorized'}), 401

        drive_client = GoogleDriveClient(token_record)
        files = drive_client.list_pdf_files()

        return jsonify({'files': files}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Document Management Routes
@app.route('/api/documents', methods=['GET'])
@login_required
def get_documents():
    """Get all documents for current user"""
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.created_at.desc()).all()
    return jsonify({'documents': [doc.to_dict() for doc in documents]}), 200


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    """Get specific document with summaries"""
    document = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    summaries = Summary.query.filter_by(document_id=doc_id).order_by(Summary.chapter_number).all()

    return jsonify({
        'document': document.to_dict(),
        'summaries': [summary.to_dict() for summary in summaries]
    }), 200


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    """Delete a document and its file"""
    document = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    try:
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete from database (cascade will delete summaries)
        db.session.delete(document)
        db.session.commit()

        return jsonify({'message': 'Document deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Job Status Routes
@app.route('/api/jobs/<job_id>/status', methods=['GET'])
@login_required
def get_job_status(job_id):
    """Get job status and progress"""
    from tasks import get_job_status as get_rq_job_status
    status = get_rq_job_status(job_id)
    return jsonify(status), 200


# Database initialization
@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
def create_admin():
    """Create admin user"""
    admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()

    if admin:
        print(f"Admin user '{app.config['ADMIN_USERNAME']}' already exists!")
        return

    admin = User(username=app.config['ADMIN_USERNAME'])
    admin.set_password(app.config['ADMIN_PASSWORD'])

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user '{app.config['ADMIN_USERNAME']}' created successfully!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
