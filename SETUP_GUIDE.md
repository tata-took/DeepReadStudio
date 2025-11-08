# DeepRead Studio - Setup Guide

This guide provides detailed instructions for setting up DeepRead Studio in various environments.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Setup](#docker-setup)
3. [Google Drive Integration](#google-drive-integration)
4. [OpenAI API Configuration](#openai-api-configuration)
5. [PythonAnywhere Deployment](#pythonanywhere-deployment)
6. [Production Deployment](#production-deployment)

---

## Local Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Redis 7 or higher
- Tesseract OCR (for scanned PDFs)
- Poppler (for PDF to image conversion)

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3-pip \
    redis-server \
    tesseract-ocr \
    tesseract-ocr-jpn \
    poppler-utils
```

**macOS:**
```bash
brew install python@3.10 redis tesseract poppler
```

**Windows:**
- Install Python from python.org
- Install Redis using WSL or Windows port
- Install Tesseract from GitHub releases
- Install Poppler from oschwartz10612/poppler-windows

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/DeepReadStudio.git
cd DeepReadStudio
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp ../.env.example ../.env

# Edit .env with your credentials
nano ../.env  # or use your preferred editor
```

### 4. Initialize Database

```bash
# Initialize database schema
flask init-db

# Create admin user
flask create-admin
```

### 5. Start Backend Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - RQ Worker:**
```bash
cd backend
source venv/bin/activate
python tasks.py
```

**Terminal 3 - Flask App:**
```bash
cd backend
source venv/bin/activate
python app.py
```

Backend will be available at: http://localhost:5000

### 6. Frontend Setup

```bash
# New terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Docker Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Build and Start

```bash
# Build images and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Initialize Database

```bash
# Create database tables
docker-compose exec backend flask init-db

# Create admin user
docker-compose exec backend flask create-admin
```

### 4. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Redis: localhost:6379

### 5. Common Docker Commands

```bash
# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View backend logs
docker-compose logs -f backend

# View worker logs
docker-compose logs -f worker

# Shell into backend container
docker-compose exec backend bash

# Restart a service
docker-compose restart backend
```

---

## Google Drive Integration

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Enter project name: "DeepRead Studio"
4. Click "Create"

### 2. Enable Google Drive API

1. In the project dashboard, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in application information:
   - App name: DeepRead Studio
   - User support email: your@email.com
   - Developer contact: your@email.com
4. Add scopes:
   - `https://www.googleapis.com/auth/drive.readonly`
5. Add test users (your email)
6. Save and continue

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application"
4. Name: "DeepRead Studio Web Client"
5. Authorized redirect URIs:
   - Development: `http://localhost:5000/oauth2callback`
   - Production: `https://yourdomain.com/oauth2callback`
6. Click "Create"
7. Copy Client ID and Client Secret

### 5. Update Environment Variables

```bash
# Edit .env file
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback
```

### 6. Test Integration

1. Start the application
2. Login to DeepRead Studio
3. Click "Google Drive" upload mode
4. Click "Authorize Google Drive"
5. Complete OAuth flow
6. You should see your PDF files listed

---

## OpenAI API Configuration

### 1. Get API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or login
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (you won't see it again!)

### 2. Add to Environment

```bash
# Edit .env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo
```

### 3. Verify Setup

```bash
# Test in Python
python3 << EOF
from openai import OpenAI
client = OpenAI(api_key='your-key-here')
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Test"}],
    max_tokens=10
)
print(response.choices[0].message.content)
EOF
```

### 4. Cost Management

- Set usage limits in OpenAI dashboard
- Monitor usage regularly
- Consider using GPT-3.5-turbo for testing (cheaper)

---

## PythonAnywhere Deployment

### 1. Sign Up

1. Go to [PythonAnywhere](https://www.pythonanywhere.com/)
2. Create account (Hacker plan recommended: $5/month)

### 2. Upload Code

**Option A: Git (Recommended)**
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/DeepReadStudio.git
cd DeepReadStudio
```

**Option B: Upload Files**
- Use Files tab to upload zip
- Extract in desired location

### 3. Run Setup Script

```bash
cd DeepReadStudio
chmod +x deploy/setup_pythonanywhere.sh
./deploy/setup_pythonanywhere.sh
```

### 4. Configure Web App

1. Go to Web tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Python version: 3.10
5. Click through to finish

### 5. Configure WSGI File

1. Click on WSGI configuration file link
2. Replace contents with:

```python
import sys
import os

# Update with your username
project_home = '/home/YOUR_USERNAME/DeepReadStudio'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

backend_path = os.path.join(project_home, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

from app import app as application
```

### 6. Set Virtual Environment

1. In Web tab, find "Virtualenv" section
2. Enter path: `/home/YOUR_USERNAME/deepread-venv`
3. Save

### 7. Configure Static Files

1. URL: `/static/`
2. Directory: `/home/YOUR_USERNAME/DeepReadStudio/frontend/dist`

### 8. Set Up Environment Variables

```bash
# In Bash console
cd DeepReadStudio
nano .env

# Add your production credentials
# Save and exit (Ctrl+X, Y, Enter)
```

### 9. Reload Web App

Click "Reload" button in Web tab

### 10. Access Your Site

Visit: https://YOUR_USERNAME.pythonanywhere.com

---

## Production Deployment

### VPS Deployment (Ubuntu 22.04)

#### 1. Server Setup

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Create app user
sudo useradd -m -s /bin/bash deepread
sudo usermod -aG docker deepread
```

#### 2. Deploy Application

```bash
# Switch to app user
sudo su - deepread

# Clone repository
git clone https://github.com/yourusername/DeepReadStudio.git
cd DeepReadStudio

# Configure environment
cp .env.example .env
nano .env  # Add production credentials

# Start services
docker-compose up -d
```

#### 3. Set Up Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt-get install nginx

# Create config
sudo nano /etc/nginx/sites-available/deepread
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/deepread /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Set Up SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

#### 5. Set Up Monitoring

```bash
# Install monitoring (optional)
docker run -d \
  --name=prometheus \
  -p 9090:9090 \
  prom/prometheus

docker run -d \
  --name=grafana \
  -p 3001:3000 \
  grafana/grafana
```

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :5000
# Kill process
kill -9 <PID>
```

**Docker permission denied:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Database locked:**
```bash
# Stop all services
docker-compose down
# Remove database
rm data/deepread.db
# Restart and reinitialize
docker-compose up -d
docker-compose exec backend flask init-db
```

**Redis connection refused:**
```bash
# Check Redis is running
docker-compose ps redis
# Restart Redis
docker-compose restart redis
```

---

## Next Steps

After setup:

1. Change default admin password
2. Configure backup strategy
3. Set up monitoring and logging
4. Review security settings
5. Test document processing
6. Configure Google Drive integration
7. Set up usage alerts for OpenAI API

For additional help, see README.md or open an issue on GitHub.
