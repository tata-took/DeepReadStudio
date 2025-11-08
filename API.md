# DeepRead Studio API Documentation

Base URL: `http://localhost:5000/api`

All endpoints require authentication except where noted.

## Authentication

### Login

**POST** `/auth/login`

Login with username and password.

**Request:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin"
  }
}
```

**Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

---

### Logout

**POST** `/auth/logout`

Logout current user.

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

### Check Auth Status

**GET** `/auth/status`

Check if user is authenticated. No authentication required.

**Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "username": "admin"
  }
}
```

---

## Document Upload

### Upload Local File

**POST** `/upload/local`

Upload PDF file from local storage.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response (201):**
```json
{
  "message": "File uploaded successfully",
  "document": {
    "id": 1,
    "filename": "document.pdf",
    "file_hash": "abc123...",
    "file_size": 1024000,
    "source_type": "local",
    "status": "pending",
    "progress": 0,
    "total_pages": null,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00",
    "completed_at": null,
    "error_message": null
  },
  "job_id": "job-uuid-here"
}
```

**Response (400):**
```json
{
  "error": "No file part"
}
// OR
{
  "error": "File type not allowed. Only PDF files are accepted"
}
```

---

### Upload from Google Drive

**POST** `/upload/google-drive`

Upload PDF file from Google Drive.

**Request:**
```json
{
  "file_id": "google-drive-file-id"
}
```

**Response (201):**
```json
{
  "message": "File downloaded from Google Drive successfully",
  "document": {
    "id": 2,
    "filename": "document.pdf",
    "file_hash": "def456...",
    "file_size": 2048000,
    "source_type": "google_drive",
    "google_drive_id": "google-drive-file-id",
    "status": "pending",
    "progress": 0,
    "total_pages": null,
    "created_at": "2024-01-01T12:00:00"
  },
  "job_id": "job-uuid-here"
}
```

**Response (400):**
```json
{
  "error": "Google Drive file ID required"
}
```

**Response (401):**
```json
{
  "error": "Google Drive not authorized"
}
```

---

## Document Management

### Get All Documents

**GET** `/documents`

Get all documents for current user.

**Response (200):**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "document.pdf",
      "file_hash": "abc123...",
      "file_size": 1024000,
      "source_type": "local",
      "status": "completed",
      "progress": 100,
      "total_pages": 150,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:30:00",
      "completed_at": "2024-01-01T12:30:00",
      "error_message": null
    }
  ]
}
```

---

### Get Document Details

**GET** `/documents/:id`

Get specific document with summaries.

**Response (200):**
```json
{
  "document": {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 1024000,
    "status": "completed",
    "progress": 100,
    "total_pages": 150
  },
  "summaries": [
    {
      "id": 1,
      "summary_type": "overall",
      "chapter_number": null,
      "chapter_title": null,
      "start_page": null,
      "end_page": null,
      "content": "This document discusses...",
      "keywords": "AI, machine learning, deep learning",
      "created_at": "2024-01-01T12:30:00"
    },
    {
      "id": 2,
      "summary_type": "chapter",
      "chapter_number": 1,
      "chapter_title": "Introduction",
      "start_page": 0,
      "end_page": 10,
      "content": "Chapter 1 introduces...",
      "keywords": "introduction, overview",
      "created_at": "2024-01-01T12:25:00"
    }
  ]
}
```

**Response (404):**
```json
{
  "error": "Document not found"
}
```

---

### Delete Document

**DELETE** `/documents/:id`

Delete a document and its file.

**Response (200):**
```json
{
  "message": "Document deleted successfully"
}
```

**Response (404):**
```json
{
  "error": "Document not found"
}
```

---

## Google Drive Integration

### Get Authorization URL

**GET** `/google-drive/auth-url`

Get Google OAuth authorization URL.

**Response (200):**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

---

### Handle OAuth Callback

**POST** `/google-drive/callback`

Exchange authorization code for access token.

**Request:**
```json
{
  "code": "authorization-code-from-google"
}
```

**Response (200):**
```json
{
  "message": "Google Drive authorized successfully"
}
```

**Response (400):**
```json
{
  "error": "Authorization code required"
}
```

---

### List Google Drive Files

**GET** `/google-drive/files`

List PDF files from Google Drive.

**Response (200):**
```json
{
  "files": [
    {
      "id": "file-id-1",
      "name": "document1.pdf",
      "size": 1024000,
      "modified_time": "2024-01-01T12:00:00",
      "mime_type": "application/pdf"
    },
    {
      "id": "file-id-2",
      "name": "document2.pdf",
      "size": 2048000,
      "modified_time": "2024-01-02T12:00:00",
      "mime_type": "application/pdf"
    }
  ]
}
```

**Response (401):**
```json
{
  "error": "Google Drive not authorized"
}
```

---

## Job Status

### Get Job Status

**GET** `/jobs/:job_id/status`

Get processing job status and progress.

**Response (200):**
```json
{
  "job_id": "job-uuid-here",
  "status": "started",
  "created_at": "2024-01-01T12:00:00",
  "started_at": "2024-01-01T12:00:01",
  "ended_at": null,
  "result": null,
  "exc_info": null,
  "progress": 45
}
```

**Job Statuses:**
- `queued`: Job is in queue
- `started`: Job is processing
- `finished`: Job completed successfully
- `failed`: Job failed with error

---

## Error Responses

All endpoints may return these error responses:

**400 Bad Request:**
```json
{
  "error": "Description of what went wrong"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication required"
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error description"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Recommended: 100 requests per minute per user
- Document upload: 10 requests per hour per user

---

## Data Models

### Document

```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_hash": "sha256-hash",
  "file_size": 1024000,
  "source_type": "local",
  "google_drive_id": null,
  "status": "completed",
  "progress": 100,
  "total_pages": 150,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:30:00",
  "completed_at": "2024-01-01T12:30:00",
  "error_message": null
}
```

**Status Values:**
- `pending`: Waiting to be processed
- `processing`: Currently being processed
- `completed`: Successfully processed
- `failed`: Processing failed

**Source Types:**
- `local`: Uploaded from local file
- `google_drive`: Downloaded from Google Drive

### Summary

```json
{
  "id": 1,
  "summary_type": "chapter",
  "chapter_number": 1,
  "chapter_title": "Introduction",
  "start_page": 0,
  "end_page": 10,
  "content": "Summary text...",
  "keywords": "keyword1, keyword2, keyword3",
  "created_at": "2024-01-01T12:25:00"
}
```

**Summary Types:**
- `overall`: Overall document summary
- `chapter`: Individual chapter summary

---

## Usage Examples

### cURL

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}' \
  -c cookies.txt
```

**Upload File:**
```bash
curl -X POST http://localhost:5000/api/upload/local \
  -F "file=@/path/to/document.pdf" \
  -b cookies.txt
```

**Get Documents:**
```bash
curl -X GET http://localhost:5000/api/documents \
  -b cookies.txt
```

### JavaScript (Axios)

```javascript
import axios from 'axios'

// Configure axios
axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://localhost:5000'

// Login
const login = async (username, password) => {
  const response = await axios.post('/api/auth/login', {
    username,
    password
  })
  return response.data
}

// Upload file
const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post('/api/upload/local', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

// Get documents
const getDocuments = async () => {
  const response = await axios.get('/api/documents')
  return response.data.documents
}
```

### Python (Requests)

```python
import requests

BASE_URL = 'http://localhost:5000/api'
session = requests.Session()

# Login
def login(username, password):
    response = session.post(f'{BASE_URL}/auth/login', json={
        'username': username,
        'password': password
    })
    return response.json()

# Upload file
def upload_file(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = session.post(f'{BASE_URL}/upload/local', files=files)
    return response.json()

# Get documents
def get_documents():
    response = session.get(f'{BASE_URL}/documents')
    return response.json()['documents']
```

---

## WebSocket Support (Future)

Real-time progress updates will be added in future versions using WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/progress')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log(`Progress: ${data.progress}%`)
}
```

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Document upload (local + Google Drive)
- AI summarization
- Async processing

### Planned Features
- WebSocket for real-time updates
- Batch document processing
- Export API (PDF, Word, Markdown)
- Search API
- Analytics API
