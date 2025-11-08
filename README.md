# DeepRead Studio

**AI-Powered PDF Document Summarization**

DeepRead Studio is a web application that automatically summarizes and analyzes PDF documents, helping readers "get a map before reading." It supports asynchronous processing, mobile optimization, and integrates with Google Drive for seamless document management.

## Features

- **📄 PDF Upload & Processing**
  - Local file upload (up to 100MB)
  - Google Drive integration with OAuth 2.0
  - Automatic duplicate detection using file hashing

- **🤖 AI-Powered Summarization**
  - Chapter-by-chapter summaries
  - Overall document summary
  - Keyword extraction
  - Support for scanned PDFs via OCR
  - Multimodal analysis (text + images)

- **⚡ Async Processing**
  - Background job processing with Redis + RQ
  - Real-time progress tracking
  - Non-blocking user experience

- **📱 Mobile-Optimized UI**
  - Responsive design with Tailwind CSS
  - Apple-like aesthetic
  - Touch-friendly interface

- **🔐 Security**
  - User authentication
  - Secure API key management
  - Google OAuth 2.0 integration

## Architecture

```
Frontend: React + Vite + Tailwind CSS
Backend: Flask + SQLAlchemy + RQ
Database: SQLite
Queue: Redis
AI: OpenAI GPT-4 (multimodal)
Deployment: Docker / PythonAnywhere
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)
- OpenAI API key
- Google Cloud Platform project (for Drive integration)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/DeepReadStudio.git
cd DeepReadStudio
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Google Drive OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Flask
FLASK_SECRET_KEY=your_random_secret_key

# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### 3. Run with Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Initialize database and create admin user
docker-compose exec backend flask init-db
docker-compose exec backend flask create-admin
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### 4. Run Locally (Development)

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask init-db
flask create-admin

# Start Redis (in separate terminal)
redis-server

# Start worker (in separate terminal)
python tasks.py

# Start Flask app
python app.py
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Google Drive Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Drive API

2. **Configure OAuth Consent Screen**
   - Set application name to "DeepRead Studio"
   - Add scopes: `https://www.googleapis.com/auth/drive.readonly`

3. **Create OAuth 2.0 Credentials**
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5000/oauth2callback`
   - Copy Client ID and Client Secret to `.env`

## API Documentation

### Authentication

**POST** `/api/auth/login`
```json
{
  "username": "admin",
  "password": "password"
}
```

**POST** `/api/auth/logout`

**GET** `/api/auth/status`

### Document Upload

**POST** `/api/upload/local`
- Form data: `file` (PDF file)

**POST** `/api/upload/google-drive`
```json
{
  "file_id": "google_drive_file_id"
}
```

### Document Management

**GET** `/api/documents`
- Returns list of all documents

**GET** `/api/documents/:id`
- Returns document with summaries

**DELETE** `/api/documents/:id`
- Deletes document and file

### Google Drive

**GET** `/api/google-drive/auth-url`
- Returns OAuth authorization URL

**POST** `/api/google-drive/callback`
```json
{
  "code": "authorization_code"
}
```

**GET** `/api/google-drive/files`
- Returns list of PDF files from Google Drive

### Job Status

**GET** `/api/jobs/:job_id/status`
- Returns processing job status

## Deployment

### Docker Deployment

```bash
# Production build
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### PythonAnywhere Deployment

1. **Upload Code**
```bash
git clone https://github.com/yourusername/DeepReadStudio.git
cd DeepReadStudio
```

2. **Run Setup Script**
```bash
chmod +x deploy/setup_pythonanywhere.sh
./deploy/setup_pythonanywhere.sh
```

3. **Configure Web App**
   - Go to PythonAnywhere Web tab
   - Add new web app
   - Point WSGI file to `deploy/wsgi.py`
   - Set virtualenv path: `/home/USERNAME/deepread-venv`
   - Reload web app

4. **Set Up Static Files**
   - Build frontend: `cd frontend && npm run build`
   - Configure static files mapping in PythonAnywhere

## Usage

1. **Login**
   - Use admin credentials from `.env`

2. **Upload PDF**
   - Choose "Local File" or "Google Drive"
   - Select PDF document (max 100MB)
   - Click "Upload and Process"

3. **Monitor Progress**
   - View processing status on dashboard
   - Track progress bar

4. **View Summaries**
   - Click "View Summary" when processing completes
   - Toggle between "Overall Summary" and "Chapter Summaries"
   - Review keywords and insights

## Project Structure

```
DeepReadStudio/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── config.py              # Configuration
│   ├── tasks.py               # Background tasks
│   ├── requirements.txt       # Python dependencies
│   └── utils/
│       ├── pdf_processor.py   # PDF handling
│       ├── openai_client.py   # OpenAI integration
│       └── google_drive.py    # Google Drive client
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/        # React components
│   ├── package.json
│   └── vite.config.js
├── deploy/
│   ├── pythonanywhere_deploy.py
│   ├── wsgi.py
│   └── setup_pythonanywhere.sh
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.frontend
├── nginx.conf
├── .env.example
└── README.md
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend
black backend/
flake8 backend/

# Frontend
npm run lint
```

## Troubleshooting

### Redis Connection Error
```bash
# Ensure Redis is running
redis-cli ping  # Should return PONG
```

### OpenAI API Errors
- Check API key in `.env`
- Verify account has credits
- Check rate limits

### Google Drive Authorization Failed
- Verify OAuth credentials
- Check redirect URI matches exactly
- Ensure Drive API is enabled

### PDF Processing Stuck
- Check worker is running: `docker-compose logs worker`
- Verify Redis connection
- Check OpenAI API status

## Cost Estimation

For a 300-page PDF:
- **OpenAI API**: ~$0.50 - $2.00 per document
- **Storage**: Minimal (SQLite + file storage)
- **Hosting**:
  - PythonAnywhere: $5/month (Hacker plan)
  - Docker VPS: $5-10/month

## Roadmap

- [ ] Enhanced figure/table recognition
- [ ] Multiple summary types (Q&A, keywords)
- [ ] Text-to-speech integration
- [ ] Google Drive folder monitoring
- [ ] Multi-user support
- [ ] Export to PDF/Word
- [ ] Comparison view for multiple documents

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/DeepReadStudio/issues
- Email: support@deepreadstudio.com

## Acknowledgments

- OpenAI for GPT-4 API
- Google for Drive API
- All open-source contributors

---

**Built with ❤️ for better reading experiences**
